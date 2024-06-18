# 2024-1 컴퓨터네트워크특강(4190.778) Team 8
- 조원 : 이정범([jeremy3599@snu.ac.kr](jeremy3599@snu.ac.kr)), 송수빈([sbsong66@snu.ac.kr](sbsong66@snu.ac.kr))

- 주제 : Tor website fingerprinting defense using HTTP/3 (QUIC)

## References

Payap Sirinam, Mohsen Imani, Marc Juarez, and Matthew Wright. 2018. Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep Learning. In 2018 ACM SIGSAC Conference on Computer and Communications Security (CCS ’18), October 15–19, 2018, Toronto, ON, Canada. ACM, New York, NY, USA, 16 pages. https://doi.org/10.1145/3243734.3243768

## 실행 방법
### Prerequisites
- Docker
- tcpdump
- Python packages in [requirements.txt](requirements.txt) should be pre-installed

### 1. Data collection

먼저 `1-data-collection/.env`에 OPENVPN_USER1, OPENVPN_USER2, OPENVPN_PASSWORD1, OPENVPN_PASSWORD2, SE_VNC_PASSWORD을 설정한다. 그런 다음,

 ```bash
 $ cd 1-data-collection
 $ ./batch_docker_run.sh 20 # 도커 bridge network들 생성 및 컨테이너들 생성
 $ ./batch_capture.sh 20 # 캡쳐 시작
 ```

이렇게 입력하고 나면 20쓰레드로 캡쳐가 시작될 것이다. 어느정도 pcap file들이 모였다면 `pkill mass.sh && pkill tcpdump`로 capture process들을 종료한다.

#### Cleanup

```bash
$ ./remove_all_containers.sh # cleanup
$ docker network prune # 주의! 이 커맨드는 gluetun이랑 관련없는 network들까지 다 prune되므로, 다른 네트워크가 존재한다면 `docker network rm gluetun1` 이런식으로 직접 삭제할 것
```

### 2. Preprocessing

```bash
$ cd ../2-preprocessing
$ ./filter_openvpn.sh ../1-data-collection/pcaps/pcaps ./pcaps_ovpn # Openvpn 트래픽만 남기고 걸러냄
$ python preprocess.py ./pcaps_ovpn ./preprocessed 10 # 마지막의 "10"은 병렬 처리를 위한 thread 개수로, CPU 성능에 따라 알맞게 조절하도록 한다.

# For http2
$ python refactor_preprocessed.py ./preprocessed ../3-model-training/dataset/ClosedWorld/NoDef/http2 NoDef
# For http3
$ python refactor_preprocessed.py ./preprocessed ../3-model-training/dataset/ClosedWorld/NoDef/http3 NoDef
```

### 3. Model training

```bash
$ cd ../3-model-training/src
$ python ClosedWorld_DF_NoDef.py # 모델 훈련
$ python cross_test.py # http2, 3 cross-testing
```

훈련된 모델은 `3-model-training/saved_trained_models/` 디렉토리에, test 및 cross-test result는  `3-model-training/results/` 디렉토리에 저장된다.

## 파일 및 디렉토리 설명

- `1-data-collection/` : 데이터 수집에 사용한 코드가 포함된 디렉토리. [^3]의 코드를 기반으로 하여 많이 수정하였음 (해당 repo에서는 데이터 수집용 코드만 차용하였고 훈련 코드는 사용하지 않았음)

  - `.env` (비공개) : OPENVPN_USER1, OPENVPN_USER2, OPENVPN_PASSWORD1, OPENVPN_PASSWORD2, SE_VNC_PASSWORD 환경변수들이 설정되어 있어야 함.

  - `batch_docker_run.sh` : 크롤링에 필요한 gluetun, selenium 컨테이너들을 한번에 여러개 실행할 수 있는 스크립트. `.env`파일에 환경변수들이 적절하게 설정되어 있어야 함
  - `batch_capture.sh` : 실행중인 도커 컨테이너들을 통해서 n개의 쓰레드를 통해 병렬적으로 패킷 캡쳐 수행 (`pcaps/`) 디렉토리에 있는 파일들을 이용함
  - `pcaps/`
    - `websites.txt` : 크롤링하는 웹사이트들의 목록
    - `mass.sh` : 위의 `batch_capture.sh`에 의해 recursive하게 실행되며, 사용자가 직접 프로세스를 kill할때까지 websites.txt에 있는 사이트들을 반복적으로 크롤링하고 pcap파일로 캡쳐함. 이 과정에서 `visit_website.py`와 `capture.sh`를 사용함
      - **주의**: mass.sh는 default로 `http2` dataset을 캡쳐함. `http3` dataset을 캡쳐하고 싶다면 59행의 `python visit_website.py "https://$website" "$SELENIUM_HOST" "$SELENIUM_PORT" &`을 `python visit_website.py "https://$website" "$SELENIUM_HOST" "$SELENIUM_PORT" --http3 &` 으로 수정한 후 실행 
      - `visit_website.py` : Selenium을 이용하여 주어진 website에 방문하는 스크립트
      - `capture.sh` : tcpdump를 통해 주어진 gluetun docker bridge network의 패킷을 캡쳐하고 pcap file로 저장하는 스크립트

- `2-preprocessing/` : `1-data-collection`의 코드들을 통해 수집된 pcap 파일들을 모델 훈련의 입력으로 들어가는 형태로 전처리하는 코드들의 모음

  - `filter_openvpn.sh` : 입력으로 주어진 디렉토리의 모든 pcap 파일들의 내용을, OpenVPN 트래픽만 남기도록 필터링하여 새로운 디렉토리로 output하는 스크립트
  - `preprocess.py` : 입력 디렉토리에 있는 pcap 파일들로부터 특성을 추출하여, 웹사이트별로 `[n*5000]` dimension의 numpy array로 저장함 (파일명: `features.pkl`)
  - `refactor_preprocessed.py` : 위의 `preprocess.py`의 출력으로 나온 디렉토리를 input으로 받아서, DF 모델 training에 직접적으로 이용될 수 있는 형태로 변환함. train/test split 역시 이 단계에서 처리됨

- `3-model-training/` : 모델 훈련에 사용한 코드가 포함된 디렉토리. DF 논문의 오픈소스 코드, 즉[^2]을 거의 그대로 사용하였음. 다만 기존 코드가 python 2, tensorflow 1을 사용하고 있어서, 버전만 python 3, tensorflow 2로 refactor함 

  - `dataset/` : ` 2-preprocessing/refactor_preprocessed.py` 의 출력으로 나온 dataset들을 포함하는 디렉토리. `http2/`, `http3/` 이렇게 두 subdirectory를 가지며 각각에 대한 알맞은 dataset을 포함하고 있어야 함. 실제 우리가 수집하여 훈련에 사용한 dataset은 크기가 커서 [MMLAB synology의 이 링크](https://snu-cse-mmlab.synology.me/drive/d/f/yvqsEl5ZZ93nHKV5gqKOLPRYGmQXpp3W)에 공유함
  - `src/` : 훈련에 사용되는 코드를 포함하는 디렉토리
    - `ClosedWorld_DF_NoDef.py` : 모델 훈련을 실행하는 코드. `python ClosedWorld_DF_NoDef.py`와 같이 실행하면 됨
      - `Model_NoDef.py`, `utility.py` : `ClosedWorld_DF_NoDef.py`에 의해 사용되는 모듈들이며 직접 실행할 필요는 없음

    -  `cross_test.py` : http2, http3 model들과 test dataset들을 cross-test하는 스크립트

  - `saved_trained_models/` : `ClosedWorld_DF_NoDef.py`의 훈련 결과로 나온 두 모델들이 저장되는 디렉토리. 실제 우리의 실험 결과로 나온 모델들은 크기가 커서 [MMLAB synology의 이 링크](https://snu-cse-mmlab.synology.me/drive/d/f/yvqs5G5uf2h07sWJwtsnt2iXPiEVGKVP)에 공유함
  - `results/` : http2, http3 model test result와 cross test result가 저장되는 디렉토리
    - `plot_results.ipynb` : 모델 훈련 과정 및 테스트, cross-test 결과의 accuracy/loss를 가지고 그래프를 그리는 코드



[^1]: Payap Sirinam, Mohsen Imani, Marc Juarez, and Matthew Wright. 2018. Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep Learning. In 2018 ACM SIGSAC Conference on Computer and Communications Security (CCS ’18), October 15–19, 2018, Toronto, ON, Canada. ACM, New York, NY, USA, 16 pages. https://doi.org/10.1145/3243734.3243768
[^2]: [deep-fingerprinting/df: The source code and dataset are used to demonstrate the DF model, and reproduce the results of the ACM CCS2018 paper](https://github.com/deep-fingerprinting/df)
[^3]: [wisepythagoras/website-fingerprinting: Deanonymizing Tor or VPN users with website fingerprinting and machine learning.](https://github.com/wisepythagoras/website-fingerprinting)

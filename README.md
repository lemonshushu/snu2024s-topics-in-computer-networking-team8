# 2024-1 컴퓨터네트워크특강(4190.778) Team 8
- 조원 : 이정범([jeremy3599@snu.ac.kr](jeremy3599@snu.ac.kr)), 송수빈([sbsong66@snu.ac.kr](sbsong66@snu.ac.kr))

- 주제 : Tor website fingerprinting defense using HTTP/3 (QUIC)

## References
Payap Sirinam, Mohsen Imani, Marc Juarez, and Matthew Wright. 2018. Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep Learning. In 2018 ACM SIGSAC Conference on Computer and Communications Security (CCS ’18), October 15–19, 2018, Toronto, ON, Canada. ACM, New York, NY, USA, 16 pages. https://doi.org/10.1145/3243734.3243768
## 파일 및 디렉토리 설명

- `data-collection/` : 데이터 수집에 사용한 코드가 포함된 디렉토리. [^3]의 코드를 기반으로 하여 많이 수정하였음

- `model-training/` : 모델 훈련에 사용한 코드가 포함된 디렉토리. [^2]의 코드를 거의 그대로 사용하였음. 다만 기존 코드가 python 2, tensorflow 1을 사용하고 있어서, 버전만 python 3, tensorflow 2로 refactor함 

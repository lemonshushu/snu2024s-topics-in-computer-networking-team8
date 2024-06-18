import pickle
from tensorflow import keras
from keras.utils import to_categorical

http2_model_path = "saved_trained_models/NoDef_http2.h5"
http3_model_path = "saved_trained_models/NoDef_http3.h5"

http2_test_x = "dataset/ClosedWorld/NoDef/http2/X_test_NoDef.pkl"
http2_test_y = "dataset/ClosedWorld/NoDef/http2/y_test_NoDef.pkl"
http3_test_x = "dataset/ClosedWorld/NoDef/http3/X_test_NoDef.pkl"
http3_test_y = "dataset/ClosedWorld/NoDef/http3/y_test_NoDef.pkl"

# Load the test data
with open(http2_test_x, "rb") as f:
    X_test_http2 = pickle.load(f)
with open(http2_test_y, "rb") as f:
    y_test_http2 = pickle.load(f)
with open(http3_test_x, "rb") as f:
    X_test_http3 = pickle.load(f)
with open(http3_test_y, "rb") as f:
    y_test_http3 = pickle.load(f)

# Convert labels to one-hot encoding
num_classes = 101  # Adjust this based on your specific number of classes
y_test_http2 = to_categorical(y_test_http2, num_classes)
y_test_http3 = to_categorical(y_test_http3, num_classes)

# Load the trained models
model_http2 = keras.models.load_model(http2_model_path)
model_http3 = keras.models.load_model(http3_model_path)

# 1. Evaluate http2 test data on http2 model
score_http2_on_http2 = model_http2.evaluate(X_test_http2, y_test_http2, verbose=1)
print("Testing loss and accuracy for http2 model:", score_http2_on_http2)

# 2. Evaluate http3 test data on http2 model
score_http3_on_http2 = model_http2.evaluate(X_test_http3, y_test_http3, verbose=1)
print("Testing loss and accuracy for http3 data on http2 model:", score_http3_on_http2)

# 3. Evaluate http3 test data on http3 model
score_http3_on_http3 = model_http3.evaluate(X_test_http3, y_test_http3, verbose=1)
print("Testing loss and accuracy for http3 model:", score_http3_on_http3)

# 4. Evaluate http2 test data on http3 model
score_http2_on_http3 = model_http3.evaluate(X_test_http2, y_test_http2, verbose=1)
print("Testing loss and accuracy for http2 data on http3 model:", score_http2_on_http3)

# Save result to file
with open("results/cross.txt", "w") as f:
    f.write("Testing loss and accuracy for http2 model: {}\n".format(score_http2_on_http2))
    f.write("Testing loss and accuracy for http3 data on http2 model: {}\n".format(score_http3_on_http2))
    f.write("Testing loss and accuracy for http3 model: {}\n".format(score_http3_on_http3))
    f.write("Testing loss and accuracy for http2 data on http3 model: {}\n".format(score_http2_on_http3))

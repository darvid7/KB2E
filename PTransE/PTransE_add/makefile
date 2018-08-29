all: train_path test_path

train_path: Train_TransE_path.cpp
	g++ Train_TransE_path.cpp -o Train_TransE_path -O2
train_RNN: Train_TransE_RNN.cpp
	g++ Train_TransE_RNN.cpp -o Train_TransE_RNN -O2
test_path: Test_TransE_path.cpp
	g++ Test_TransE_path.cpp -o Test_TransE_path -O2

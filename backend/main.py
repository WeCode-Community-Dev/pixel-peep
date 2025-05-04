import test,train

train_folder_dir="C:/Users/Sanjay/OneDrive/Documents/pixel-peep/test_cases/train_images"
test_folder_dir="C:/Users/Sanjay/OneDrive/Documents/pixel-peep/test_cases/test_images"

des_list=train.train_images(folder_dir=train_folder_dir)
is_Match=test.test_images(folder_dir=test_folder_dir,des_from_train=des_list)

for matches in is_Match:
    print(matches,sep="\n")
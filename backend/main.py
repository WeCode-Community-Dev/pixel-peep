import test,train

folder_dir1="C:/Users/Sanjay/OneDrive/Documents/pixel-peep/test_cases/train_images"
folder_dir2="C:/Users/Sanjay/OneDrive/Documents/pixel-peep/test_cases/test_images"

des_list=train.train_images(folder_dir=folder_dir1)
is_Match=test.test_images(folder_dir=folder_dir2,des_from_train=des_list)

for matches in is_Match:
    print(matches,sep="\n")
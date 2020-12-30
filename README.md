# crf kr version

현재 토크나이저 추가 구현 중



# Usage

current train_file must have form like ( will modify soon ):

한	한/MM   
번	번/NNB   
쓰고	쓰/VV+고/EC   
말	말/VX+ㄹ/ETM   
그런	그런/MM   
무미건조한	무미건조/NNG+하/XSA+ㄴ/ETM   
답이	답/NNG+이/JKS   
정답(正答)이라고	정답/NNG+(/SS+正答/SH+)/SS+이/VCP+라고/EC   
세상에	세상/NNG+에/JKB   
유통이	유통/NNG+이/JKC   
되는	되/VV+는/ETM   
한	한/NNG   
동지잔치나	동지/NNG+잔치/NNG+나/JC   
동지팥죽을	동지/NNG+팥죽/NNG+을/JKO   
설명하기	설명/NNG+하/XSV+기/ETN   
어렵다.	어렵/VA+다/EF+./SF   
   
or   
한  MM   
번  NNB   
쓰  VV   
고  EC   
말  VX
그  MM
런  MM
...



# train or test

python crf_kr.py <train_file> <model_file> <mode(train or test)> <batch boolean>







# 참조 코드

https://github.com/lancifollia/crf



# License

MIT



## Reference

An Introduction to Conditional Random Fields / Charles Sutton, Andrew McCallum/ 2010


# CRF kr

---

- CRF that can train and inference with kr

- author: ChanYang Park

- version: 1.0 (2021/06/07)

---

# Needed Library

- math
- numpy
- scipy.optimize
- time
- json
- datetime
- sys
- collections
- nltk_ko
- re
- argparse



# Usage

---

- ### Train   



![image-20210107171606343](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20210107171606343.png)



- ### Inference



### Inference with sentense



![image-20210107171702294](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20210107171702294.png)



### Inference with sentense file

![image-20210107171746039](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20210107171746039.png)


---



# Input, Output



---

- ### Train Input



input file should be like:

```
노	NNG
랭	NNG
이	NNG
는	JX
집	NNG
에	JKB
없	VA
어	EC
요	EC

노	NNG
랭	NNG
이	NNG
다	MM
른	MM
집	NNG
에	JKB
갔	CO
댄	CO
다	EC
```







output is model file



- ### Inference input



#### Inference sentense

> #### Input
> you can handle just one sentense
>
> like this:
>
> ![image-20210107171702294](C:\Users\user\AppData\Roaming\Typora\typora-user-images\image-20210107171702294.png)
>
> 
>
> 
>
> 
>
> #### Output
>
> 
>
> [('이', 'NP'), ('것', 'NP'), ('은', 'JX'), ('문', 'NNG'), ('장', 'NNG'), ('입', 'CO'), ('니', 'EC'), ('다', 'EC')]





#### infrence file

> ### input
>
> 
>
> ```
> 종적을 감춘 송흥록이 떠난 곳도 거기다.
> 모든 존재와 아름다움과 그리움의 근원이다
> ```
>
> 
>
> 
>
> ### output
>
> 
>
> output tagged pos can be changed based on trained data
>
> output file saved on ./modelname.result
>
> ex)
>
> ```
> 양반네들	양/NN+반/NS+네/NN+들/XN
> 앞에서	앞/NS+에/JJ+서/JJ
> 그네들	그/NS+네/NN+들/XN
> 조롱하는	조/NS+롱/NN+하/XV+는/EE
> 소리	소/NS+리/NN
> ```
>
> 
>





---





## Reference Code

https://github.com/lancifollia/crf



## License

MIT



## Reference

An Introduction to Conditional Random Fields / Charles Sutton, Andrew McCallum/ 2010


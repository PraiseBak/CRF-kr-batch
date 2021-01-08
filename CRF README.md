# CRF README

- 필요 라이브러리

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

- 학습

  - ```
    from crf import LinearChainCRF
    crf = LinearChainCRF()
    crf.train(filename,modelname)
    ```

  - input - 입력 코퍼스

    ```
    한	MM
    번	NNB
    쓰	VV
    고	EC
    말	VX
    그	MM
    런	MM
    무	NNG
    미	NNG
    건	NNG
    조	NNG
    한	CO
    답	NNG
    이	JKS
    정	NNG
    답	NNG
    (	SS
    正	SH
    答	SH
    )	SS
    이	VCP
    라	EC
    고	EC
    세	NNG
    상	NNG
    에	JKB
    유	NNG
    통	NNG
    이	JKC
    되	VV
    는	ETM
    한	NNG
    동	NNG
    지	NNG
    잔	NNG
    치	NNG
    나	JC
    동	NNG
    지	NNG
    팥	NNG
    죽	NNG
    을	JKO
    설	NNG
    명	NNG
    하	XSV
    기	ETN
    어	VA
    렵	VA
    다	EF
    .	SF
    
    그	NNG
    날	NNG
    그	NNG
    날	NNG
    공	NNG
    장	NNG
    에	JKB
    서	JKB
    들	VV
    어	VV
    온	CO
    물	NNG
    품	NNG
    과	JC
    매	NNG
    장	NNG
    에	JKB
    나	VV
    간	CO
    물	NNG
    품	NNG
    을	JKO
    기	NNG
    록	NNG
    하	XSV
    고	EC
    ,	SP
    공	NNG
    장	NNG
    별	XSN
    로	JKB
    매	NNG
    입	NNG
    가	XSN
    의	JKG
    대	NNG
    차	NNG
    대	NNG
    조	NNG
    표	NNG
    를	JKO
    만	VV
    들	VV
    었	EP
    다	EF
    .	SF
    ```

    

  - output - 모델

    - modelname의 경로에 modelname.json 파일이 생성됩니다

- 추론

  - ```
    from crf import LinearChainCRF
    crf = LinearChainCRF()
    crf.inference_sentense("문장입니다",modelname)
    
    ```

    - modelname - 추론에 사용할 모델 경로
    - return [(음절,형태소), ... ]

    

  - ```
    from crf import LinearChainCRF
    crf = LinearChainCRF()
    crf.only_inference(filename,modelname)
    
    ```

    - 추론한 결과는 modelname.result에 저장됩니다


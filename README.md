# Depth_Focusing

## 목표
- 현실 세계에는 사진을 변환시키는 컨텐츠가 다양하게 사용되고 있습니다.
- 우리의 프로그램은, 그러한 컨텐츠를 위해 사진을 객체와 깊이(depth) 별로 포커싱 하는 프로그램이다.
- 최종적으로 우리의 프로그램을 모바일에서 사용되어지도록 모델을 구성할 것이다.


## 모델 설명
1. 현실세계의 사진을 입력으로 받는다.
2. 사진에 대한 깊이와 객체 분할을 추출한다.
> 자연의 사물과 사람의 사물에 대한 사진을 촬영할 것으로 예상되기에, COCO Dataset으로 학습시킨 모델을 선정한다.

## 기술 스택
### 프론트엔드
| JavaScript | TypeScript |  React   |  Node   |
| :--------: | :--------: | :------: | :-----: |
### 백엔드
|   python   |   Django   |
| :--------: | :--------: |
### 딥러닝모델
|   Adabins  | Mask2Former|
| :--------: | :--------: |

## 구현 방식
 - 개발환경 : Poetry --version 1.2.0
 - 배포 : Poetry와의 호환성을 위해 **Render**를 통해 배포
 - ORM 기반 코드
 - DRF를 이용한 RESTful API 설계 및 구현
 - Cloudflare API를 통한 이미지 저장
 - github API를 통한 로그인 기능 구현

## 최종 결과
- 사진의 특정 물체를 객체 분할을 통해 선택하고, 해당 물체의 깊이에 따라 해당 물체를 제외한 모든 것(배경 포함)들에 블러 처리를 해준다.

#### Frontend : https://github.com/SonJinHYo/Depth_Focusing_Frontend
#### Site : https://depth-focusing.xyz

##### 23-02-10 이사 완료 (이전 주소:https://github.com/Kihwan-Ryoo/Depth_Focusing)

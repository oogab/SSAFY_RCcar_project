# SSAFY_RCcar_project
Raspberry Pi를 이용한 RCcar 제작 프로젝트입니다.  

SSAFY Embedded반 1학기 최종 프로젝트입니다.
기본적인 RCcar를 구현하였으며 디스플레이의 명령 버튼을 통해 DB로 명령 전달   
RCcar에서 DB의 명령을 읽어와 수행하는 방식입니다.   

ServoMotor와 Sonar sensor를 활용하여 포신 처럼 작동하는 부분을 부착하였습니다.  
디스플레이의 Shoot 버튼 클릭시 대상 물체와의 거리를 측정   
일정 구간 이하면 명중했다고 판단하여 디스플레이에 명중하였음을 표시합니다.

원래는 IR Sensor를 통해 맞거나 빗맞음을 측정하려 했지만...   
IR Sensor의 성능이 생각보다 너무 떨어지는 관계로 위의 방식으로 대체했습니다.   

명중 횟수를 카운트하고 이를 시각화하는 웹 대시보드를 만들어   
Tank Battle Simulator를 만들고자 했지만... 시간 문제로 웹 대시보드는 나중에 구현 예정입니다.   

Raspberry Pi  
PyQT5    
Python  
MySQL  

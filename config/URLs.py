# Desc: URL配置文件

# 运动打卡CourseId
SportsCourseId = "1828599707263381506"

# webvpn
webvpn_login_url = "https://webvpn.xjtu.edu.cn/login?oauth_login=true"
webvpn_url = "https://webvpn.xjtu.edu.cn"

# 交大研究生体美劳育管理平台 (手机版)
# 登陆跳转
tmlyglpt_login_url = "https://org.xjtu.edu.cn/openplatform/oauth/authorize?appId=1532&redirectUri=https://ipahw.xjtu.edu.cn/sso/callback&responseType=code&scope=user_info&state=1234"
# 我的活动
tmlyglpt_wdhd_url = "https://ipahw.xjtu.edu.cn/pages/index/wdhd"
# 我的活动-运动签到
tmlyglpt_ydqd_url = f"https://ipahw.xjtu.edu.cn/pages/index/hdgl/hdgl_run?courseType=7&signType=1&activityAddress=&courseInfoId={SportsCourseId}"
# 我的活动-运动签退
tmlyglpt_ydqt_url = f"https://ipahw.xjtu.edu.cn/pages/index/hdgl/hdgl_run?courseType=7&signType=2&activityAddress=&courseInfoId={SportsCourseId}"
# 接口
tmlyglpt_ydxx_api = "https://ipahw.xjtu.edu.cn/szjy-boot/api/v1/sportActa/findPage?pageNo=1&pageSize=10&sportType_EQ=2&createTime_ORDER=DESC&courseInfoId_EQ={SportsCourseId}&no_EQ={username}"
tmlyglpt_ydqd_api = "https://ipahw.xjtu.edu.cn/szjy-boot/api/v1/sportActa/signRun"
tmlyglpt_ydqt_api = "https://ipahw.xjtu.edu.cn/szjy-boot/api/v1/sportActa/signOutTrain"

# 交大研究生综合评教系统登录
yjszhpjxt_login_url = "https://org.xjtu.edu.cn/openplatform/oauth/authorizeCas?state=xjdCas&redirectUri=https://cas.xjtu.edu.cn/login?TARGET=http://gste.xjtu.edu.cn/login.do"
yjszhpjxt_url = "http://gste.xjtu.edu.cn/app/sshd4Stu/index.do"

# 交大研究生管理信息系统
yjsglxxxt_login_url = "https://org.xjtu.edu.cn/openplatform/oauth/authorize?appId=1036&state=abcd1234&redirectUri=http://gmis.xjtu.edu.cn/pyxx/sso/login&responseType=code&scope=user_info"
yjsglxxxt_url = "http://gmis.xjtu.edu.cn/pyxx/"
yjsglxxxt_wdpyjh_url = "http://gmis.xjtu.edu.cn/pyxx/pygl/pyjhcx"
yjsglxxxt_kckk_url = "http://gmis.xjtu.edu.cn/pyxx/pygl/kckk/view/new/{code}/{year}"
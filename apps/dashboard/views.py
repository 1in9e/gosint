from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from libs.common import send_to_company, send_to_mail
import json
from datetime import datetime
from apps.assets.models import Rad2xray
import demjson

# Create your views here.
class XrayWebhookView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(XrayWebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            # DONE: 接收json数据
            vuln = demjson.decode(request.body)
        except Exception as e:
            # Logging.error('json解析失败')
            print(e)
        # xray升级后，json格式完全变化
        if vuln['type'] == 'web_vuln':
            try:
                # raw = []
                # for http in vuln['data']['detail']['snapshot']:
                #     raw.append('\r\n\r\n'.join(temp for temp in http))
                Rad2xray.objects.create(addr=vuln['data']['detail']['addr'],
                                          payload=vuln['data']['detail']['payload'],
                                          # param=vuln['data']['detail']['extra']['param'],
                                          # detail=json.dumps(vuln['data']),
                                          detail='...',
                                          snapshot=vuln['data']['detail']['snapshot'][0][0],
                                          # raw='\r\n\r\n\r\n'.join(temp2 for temp2 in raw),
                                          plugin=vuln['data']['plugin'],
                                          target=vuln['data']['target']['url']),
                # web漏洞
                content = "### xray \nurl: {url} \n插件: {plugin} \n漏洞类型: {vuln_class} \n发现时间: {create_time} \n请及时查看和处理".format(
                    url=vuln["data"]["detail"]['addr'], plugin=vuln['data']["plugin"],
                    vuln_class=vuln["type"],
                    create_time=str(datetime.fromtimestamp(vuln['data']["create_time"] / 1000)))
            except Exception as e:
                # Logging.error('存储漏洞失败: 数据： {}, 错误信息：{}'.format(json.dumps(vuln), e))
                print(e)
                send_to_mail('gosint插入漏洞失败', str(e))
            # DONE： 企业微信推送 and 邮件推送
            send_to_company('gosint 发现了新漏洞', content)
            send_to_mail('gosint 发现了新漏洞', content)
        elif vuln['type'] == 'web_statistic':
            # 扫描器统计，暂不做处理
            pass
        else:
            pass
        # 新json格式
        # {
        #     "data": {
        #         "create_time": 1606109494812,
        #         "detail": {
        #             "addr": "http://testphp.vulnweb.com/",
        #             "extra": {
        #                 "param": {}
        #             },
        #             "payload": "/",
        #             "snapshot": [
        #                 [
        #                     "GET / HTTP/1.1\r\nHost: testphp.vulnweb.com\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Language: zh-CN,zh;q=0.9,ko;q=0.8\r\nCache-Control: no-cache\r\nPragma: no-cache\r\nRange: bytes=0-80960\r\nReferer: http://testphp.vulnweb.com/cart.php\r\nUpgrade-Insecure-Requests: 1\r\n\r\n",
        #                     "HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Mon, 23 Nov 2020 05:31:34 GMT\r\nServer: nginx/1.19.0\r\nX-Powered-By: PHP/5.6.40-38+ubuntu20.04.1+deb.sury.org+1\r\n\r\n\u003c!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"\n\"http://www.w3.org/TR/html4/loose.dtd\"\u003e\n\u003chtml\u003e\u003c!-- InstanceBegin template=\"/Templates/main_dynamic_template.dwt.php\" codeOutsideHTMLIsLocked=\"false\" --\u003e\n\u003chead\u003e\n\u003cmeta http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-2\"\u003e\n\n\u003c!-- InstanceBeginEditable name=\"document_title_rgn\" --\u003e\n\u003ctitle\u003eHome of Acunetix Art\u003c/title\u003e\n\u003c!-- InstanceEndEditable --\u003e\n\u003clink rel=\"stylesheet\" href=\"style.css\" type=\"text/css\"\u003e\n\u003c!-- InstanceBeginEditable name=\"headers_rgn\" --\u003e\n\u003c!-- here goes headers headers --\u003e\n\u003c!-- InstanceEndEditable --\u003e\n\u003cscript language=\"JavaScript\" type=\"text/JavaScript\"\u003e\n\u003c!--\nfunction MM_reloadPage(init) {  //reloads the window if Nav4 resized\n  if (init==true) with (navigator) {if ((appName==\"Netscape\")\u0026\u0026(parseInt(appVersion)==4)) {\n    document.MM_pgW=innerWidth; document.MM_pgH=innerHeight; onresize=MM_reloadPage; }}\n  else if (innerWidth!=document.MM_pgW || innerHeight!=document.MM_pgH) location.reload();\n}\nMM_reloadPage(true);\n//--\u003e\n\u003c/script\u003e\n\n\u003c/head\u003e\n\u003cbody\u003e \n\u003cdiv id=\"mainLayer\" style=\"position:absolute; width:700px; z-index:1\"\u003e\n\u003cdiv id=\"masthead\"\u003e \n  \u003ch1 id=\"siteName\"\u003e\u003ca href=\"https://www.acunetix.com/\"\u003e\u003cimg src=\"images/logo.gif\" width=\"306\" height=\"38\" border=\"0\" alt=\"Acunetix website security\"\u003e\u003c/a\u003e\u003c/h1\u003e   \n  \u003ch6 id=\"siteInfo\"\u003eTEST and Demonstration site for \u003ca href=\"https://www.acunetix.com/vulnerability-scanner/\"\u003eAcunetix Web Vulnerability Scanner\u003c/a\u003e\u003c/h6\u003e\n  \u003cdiv id=\"globalNav\"\u003e \n      \t\u003ctable border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\"\u003e\u003ctr\u003e\n\t\u003ctd align=\"left\"\u003e\n\t\t\u003ca href=\"index.php\"\u003ehome\u003c/a\u003e | \u003ca href=\"categories.php\"\u003ecategories\u003c/a\u003e | \u003ca href=\"artists.php\"\u003eartists\n\t\t\u003c/a\u003e | \u003ca href=\"disclaimer.php\"\u003edisclaimer\u003c/a\u003e | \u003ca href=\"cart.php\"\u003eyour cart\u003c/a\u003e | \n\t\t\u003ca href=\"guestbook.php\"\u003eguestbook\u003c/a\u003e | \n\t\t\u003ca href=\"AJAX/index.php\"\u003eAJAX Demo\u003c/a\u003e\n\t\u003c/td\u003e\n\t\u003ctd align=\"right\"\u003e\n\t\t\u003c/td\u003e\n\t\u003c/tr\u003e\u003c/table\u003e\n  \u003c/div\u003e \n\u003c/div\u003e \n\u003c!-- end masthead --\u003e \n\n\u003c!-- begin content --\u003e\n\u003c!-- InstanceBeginEditable name=\"content_rgn\" --\u003e\n\u003cdiv id=\"content\"\u003e\n\t\u003ch2 id=\"pageName\"\u003ewelcome to our page\u003c/h2\u003e\n\t  \u003cdiv class=\"story\"\u003e\n\t\t\u003ch3\u003eTest site for Acunetix WVS.\u003c/h3\u003e\n\t  \u003c/div\u003e\n\u003c/div\u003e\n\u003c!-- InstanceEndEditable --\u003e\n\u003c!--end content --\u003e\n\n\u003cdiv id=\"navBar\"\u003e \n  \u003cdiv id=\"search\"\u003e \n    \u003cform action=\"search.php?test=query\" method=\"post\"\u003e \n      \u003clabel\u003esearch art\u003c/label\u003e \n      \u003cinput name=\"searchFor\" type=\"text\" size=\"10\"\u003e \n      \u003cinput name=\"goButton\" type=\"submit\" value=\"go\"\u003e \n    \u003c/form\u003e \n  \u003c/div\u003e \n  \u003cdiv id=\"sectionLinks\"\u003e \n    \u003cul\u003e \n      \u003cli\u003e\u003ca href=\"categories.php\"\u003eBrowse categories\u003c/a\u003e\u003c/li\u003e \n      \u003cli\u003e\u003ca href=\"artists.php\"\u003eBrowse artists\u003c/a\u003e\u003c/li\u003e \n      \u003cli\u003e\u003ca href=\"cart.php\"\u003eYour cart\u003c/a\u003e\u003c/li\u003e \n      \u003cli\u003e\u003ca href=\"login.php\"\u003eSignup\u003c/a\u003e\u003c/li\u003e\n\t  \u003cli\u003e\u003ca href=\"userinfo.php\"\u003eYour profile\u003c/a\u003e\u003c/li\u003e\n\t  \u003cli\u003e\u003ca href=\"guestbook.php\"\u003eOur guestbook\u003c/a\u003e\u003c/li\u003e\n\t\t\u003cli\u003e\u003ca href=\"AJAX/index.php\"\u003eAJAX Demo\u003c/a\u003e\u003c/li\u003e\n\t  \u003c/li\u003e \n    \u003c/ul\u003e \n  \u003c/div\u003e \n  \u003cdiv class=\"relatedLinks\"\u003e \n    \u003ch3\u003eLinks\u003c/h3\u003e \n    \u003cul\u003e \n      \u003cli\u003e\u003ca href=\"http://www.acunetix.com\"\u003eSecurity art\u003c/a\u003e\u003c/li\u003e \n\t  \u003cli\u003e\u003ca href=\"https://www.acunetix.com/vulnerability-scanner/php-security-scanner/\"\u003ePHP scanner\u003c/a\u003e\u003c/li\u003e\n\t  \u003cli\u003e\u003ca href=\"https://www.acunetix.com/blog/articles/prevent-sql-injection-vulnerabilities-in-php-applications/\"\u003ePHP vuln help\u003c/a\u003e\u003c/li\u003e\n\t  \u003cli\u003e\u003ca href=\"http://www.eclectasy.com/Fractal-Explorer/index.html\"\u003eFractal Explorer\u003c/a\u003e\u003c/li\u003e \n    \u003c/ul\u003e \n  \u003c/div\u003e \n  \u003cdiv id=\"advert\"\u003e \n    \u003cp\u003e\n      \u003cobject classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\" codebase=\"http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,29,0\" width=\"107\" height=\"66\"\u003e\n        \u003cparam name=\"movie\" value=\"Flash/add.swf\"\u003e\n        \u003cparam name=quality value=high\u003e\n        \u003cembed src=\"Flash/add.swf\" quality=high pluginspage=\"http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash\" type=\"application/x-shockwave-flash\" width=\"107\" height=\"66\"\u003e\u003c/embed\u003e\n      \u003c/object\u003e\n    \u003c/p\u003e\n  \u003c/div\u003e \n\u003c/div\u003e \n\n\u003c!--end navbar --\u003e \n\u003cdiv id=\"siteInfo\"\u003e  \u003ca href=\"http://www.acunetix.com\"\u003eAbout Us\u003c/a\u003e | \u003ca href=\"privacy.php\"\u003ePrivacy Policy\u003c/a\u003e | \u003ca href=\"mailto:wvs@acunetix.com\"\u003eContact Us\u003c/a\u003e | \u003ca href=\"/Mod_Rewrite_Shop/\"\u003eShop\u003c/a\u003e | \u003ca href=\"/hpp/\"\u003eHTTP Parameter Pollution\u003c/a\u003e | \u0026copy;2019\n  Acunetix Ltd \n\u003c/div\u003e \n    \n    \n\u003cbr\u003e \n\u003cdiv style=\"background-color:lightgray;width:100%;text-align:center;font-size:12px;padding:1px\"\u003e\n\u003cp style=\"padding-left:5%;padding-right:5%\"\u003e\u003cb\u003eWarning\u003c/b\u003e: This is not a real shop. This is an example PHP application, which is intentionally vulnerable to web attacks. It is intended to help you test Acunetix. It also helps you understand how developer errors and bad configuration may let someone break into your website. You can use it to test other tools and your manual hacking skills as well. Tip: Look for potential SQL Injections, Cross-site Scripting (XSS), and Cross-site Request Forgery (CSRF), and more.\u003c/p\u003e\n\u003c/div\u003e\n\u003c/div\u003e\n\u003c/body\u003e\n\u003c!-- InstanceEnd --\u003e\u003c/html\u003e\n"]
        #             ]
        #         },
        #         "plugin": "dirscan/user/default",
        #         "target": {
        #             "url": "http://testphp.vulnweb.com/"
        #         }
        #     },
        #     "type": "web_vuln"
        # }
        return JsonResponse({'result': 'ok'})

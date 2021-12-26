Lanuages['Set the font'] = '设置字体大小';
/*SimpleuiThemes.unshift({
    "text": "dark",
    "menu": "rgb(48, 65, 86)",
    "logo": "rgb(48, 65, 86)",
    "top": "#304457",
    "file": 'dark.css',
    "main": "#304457"
})*/

window.addEventListener('load', __ => {
    NProgress.done();
    //为子页面提供进度条方法
    window.progress = NProgress;

    window.customThemeApp = new Vue({
        el: '#custom_theme',
        methods: {
            apply: function () {
                var colors = {}
                for (var key in this.props) {
                    colors[key] = this.props[key].value + "!important";
                }
                console.log(colors)
                less.modifyVars(colors);
                //存到localStore
                if (window.localStorage) {
                    localStorage['less_vars'] = JSON.stringify(colors);
                }
            }
        },
        data: {
            visible: false,
            form: {},
            props: {
                '@primary': {
                    text: '基础色',
                    type: 'color',
                    value: '#515a6e'
                },
                '@color': {
                    text: '文字颜色',
                    value: '#515A6E'
                },
                '@menu-color': {
                    text: '菜单文本颜色',
                    value: 'hsla(0, 0%, 100%, .7)'
                },
                '@menu-background': {
                    text: '菜单背景色',
                    value: '#191A23'
                },
                '@menu-color-hover': {
                    text: '菜单文本hover',
                    value: '#FFFFFF'
                },
                '@menu-background-hover': {
                    text: '菜单背景hover',
                    value: "#000000"
                },
                '@menu-title-color': {
                    text: '菜单标题文本',
                    value: 'hsla(0, 0%, 100%, .7)'
                },
                '@menu-title-background-color': {
                    text: '菜单标题背景',
                    value: '#191A23'
                },
                '@menu-title-color-hover': {
                    text: '菜单标题文本hover',
                    value: '#FFFFFF'
                },
                '@menu-title-background-color-hover': {
                    text: '菜单标题背景hover',
                    value: '#000000'
                },
                '@navbar-color': {
                    text: '导航栏文本',
                    value: '#515A6E'
                },
                '@navbar-background': {
                    text: '导航栏背景',
                    value: '#FFFFFF'
                },
                '@vip-color': {
                    text: 'Pro颜色',
                    value: '#c79c6d'
                }

            }
        }
    })
});
window.clearCache = function () {
    if (window.sessionStorage) {
        //清理tabs缓存
        delete sessionStorage['tabs'];
        delete localStorage['less_vars'];
        //清理cookie
        setCookie('theme', '');
        setCookie('theme_name', '');
        window.location.reload();
    }
}
Vue.directive('refresh', {
    bind: function (el, binding, vnode) {
        // var item = binding.value;
        // el.addEventListener('mouseenter', e => {
        //     console.log('鼠标进入')
        //     // item.hover = true;
        //     // app.$forceUpdate();
        // });
        // el.addEventListener('mouseout', e => {
        //     console.log('鼠标离开')
        //     // item.hover = false;
        //     // app.$forceUpdate();
        //     // console.log(e.target)
        // });
    }
});

var tab = {
    enter: function (item) {
        item.hover = true;
        app.$forceUpdate();
        console.log(item)
        console.log(this)
    },
    out: function (item) {
        item.hover = false;
        app.$forceUpdate();
    }
}
window.renderCallback = function (app) {
    window.js_callback = function () {
        //读取默认值 设置
        // console.log(less)
        if (window.localStorage && window.localStorage.less_vars) {
            less.modifyVars(JSON.parse(window.localStorage.less_vars));
        }
    }
    if (!app.theme || app.theme == '') {
        var id = 'simplepro_less';
        if (!document.getElementById(id)) {
            var sc = document.createElement('script');
            sc.src = less_url;
            sc.type = 'text/javascript';
            sc.id = id;
            // sc.defer = 'defer';
            document.body.append(sc);

            sc = document.createElement('script');
            sc.type = 'text/javascript';
            sc.src = js_callback_url;
            // sc.defer = 'defer';
            document.body.append(sc);

        } else {
            js_callback();
        }

    } else {
        var style = document.getElementById('less:static-admin-simpleui-x-theme-default');
        if(style){
            style.remove();
        }
    }
}
window.showCustomTheme = function () {
    customThemeApp.visible = true;
}
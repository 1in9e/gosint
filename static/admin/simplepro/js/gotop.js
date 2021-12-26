(function () {
    Vue.component('gotop', {
        data() {
            return {
                show: false
            }
        },
        methods: {
            goTo(target) {
                var scrollT = document.body.scrollTop || document.documentElement.scrollTop
                if (scrollT > target) {
                    var timer = setInterval(function () {
                        var scrollT = document.body.scrollTop || document.documentElement.scrollTop
                        var step = Math.floor(-scrollT / 30);
                        document.documentElement.scrollTop = document.body.scrollTop = step + scrollT;
                        if (scrollT <= target) {
                            document.body.scrollTop = document.documentElement.scrollTop = target;
                            clearTimeout(timer);
                        }
                    }, 5)
                } else if (scrollT == 0) {
                    var timer = setInterval(function () {
                        var scrollT = document.body.scrollTop || document.documentElement.scrollTop
                        var step = Math.floor(300 / 3 * 0.7);
                        document.documentElement.scrollTop = document.body.scrollTop = step + scrollT;
                        console.log(scrollT)
                        if (scrollT >= target) {
                            document.body.scrollTop = document.documentElement.scrollTop = target;
                            clearTimeout(timer);
                        }
                    }, 5)
                } else if (scrollT < target) {
                    var timer = setInterval(function () {
                        var scrollT = document.body.scrollTop || document.documentElement.scrollTop
                        var step = Math.floor(scrollT / 30);
                        document.documentElement.scrollTop = document.body.scrollTop = step + scrollT;
                        if (scrollT >= target) {
                            document.body.scrollTop = document.documentElement.scrollTop = target;
                            clearTimeout(timer);
                        }
                    }, 5)
                } else if (target == scrollT) {
                    return false;
                }
            }
        },
        created() {
            var self = this;
            window.document.addEventListener('scroll', e => {
                self.show = (document.documentElement.scrollTop||document.body.scrollTop) > 10;
            });
        },
        template: ' <transition name="el-fade-in"><div @click="goTo(0)" v-if="show" class="el-backtop" style="right: 40px; bottom: 40px;"><i class="el-icon-caret-top"></i></div></transition>'
    });
})();
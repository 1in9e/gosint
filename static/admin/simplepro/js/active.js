var app = new Vue({
    el: '.active',
    data: {
        dialogTableVisible: false,
        dialogActiveVisible: false,
        offlineDialogVisible: false,
        activeCode: '',
        activeLoading: false,
        dialogLoading: true,
        offlineInput: '',
        gridData: [],
        form: {},
        selectItem: null,
        pay: 'alipay',
        showQrcode: false,
        qrcodeLoading: false,
        order: {
            qrcode: null,
            orderNo: null,
            activeCode: null
        }, form: {},
        queryDialogVisible: false,
        queryDialogLoading: false,
        queryTableData: [],
    },
    created: function () {
        this.form = window.data;
        try {
            var d1 = new Date(window.data.end_date);
            var d2 = new Date();
            var day = Math.ceil((d1.getTime() - d2.getTime()) / 1000 / 60 / 60 / 24);
            this.form.last_day = day;
        } catch (e) {

        }
        var self = this;

        axios.get(_my_server + 'simplepro/package').then(res => {
            res.data.data.forEach(item => item.active = false);
            self.gridData = res.data.data;
            // if (self.gridData.length > 0) {
            // self.selectPackage(self.gridData[0]);
            // }
        }).catch(err => {
            console.log(err)
            self.$message.error('对不起，服务器遇到点小问题，不能完成操作，请稍后重试。');
        }).finally(__ => {
            self.dialogLoading = false;
        });
        setInterval(function () {
            if (self.order.orderNo && !self.order.activeCode) {
                let data = new FormData();
                data.append('order_no', self.order.orderNo);
                axios.post(_url + '/order/query', data).then(res => {
                    console.log(res)
                    if (res.data.state) {
                        self.order.activeCode = res.data.activeCode;
                        self.$message({
                            message: '付款成功，您的激活码是：' + res.data.activeCode,
                            type: 'success'
                        });
                        //弹出激活款，自动输入激活码
                        self.dialogTableVisible = false;
                        self.activeCode = self.order.activeCode;
                        self.dialogActiveVisible = true;
                    }
                })
            }
        }, 1000);
    },
    watch: {
        pay: function () {
            if (this.showQrcode) {
                this.createOrder();
            }
        }
    },
    methods: {

        offlineHandler: function () {
            var self = this;
            if (self.offlineInput.replace(/ /g, "") != "") {
                let data = new FormData();
                data.append('code', self.offlineInput);
                axios.post(_offline_active_url, data).then(res => {
                    if(res.data.state){
                        self.offlineDialogVisible = false;
                        self.$message.success(res.data.msg);
                        setTimeout(function () {
                            window.location.reload();
                        }, 1500);
                    }else{
                        self.$message.error(res.data.msg);
                    }
                });
            }
        },
        activeHandler: function () {
            this.activeLoading = true
            var self = this;
            let data = new FormData();
            data.append('active_code', self.activeCode);
            data.append('csrfmiddlewaretoken', document.getElementsByName('csrfmiddlewaretoken')[0].value);
            var url = _my_server;
            if (!url.endsWith('/')) {
                url += '/';
            }
            url += 'simplepro/active/';
            axios.post(url, data).then(res => {
                if (res.data.state) {
                    self.$message({
                        message: '激活成功，将自动刷新页面！',
                        type: 'success'
                    });
                    self.activeLoading = false;
                    setTimeout(function () {
                        window.location.reload();
                    }, 1500);
                } else {
                    self.$message.error(res.data.msg);
                }
            }).catch(err => {
                self.$message.error('对不起，服务器遇到点小问题，不能完成操作，请稍后重试。');
            }).finally(__ => {
                self.activeLoading = false;
            });
        },
        buy: function (item) {
            self.dialogBuyVisible = true
            console.log(item)
        },
        selectPackage: function (item) {
            this.gridData.forEach(k => k.active = false);
            item.active = true;
            this.selectItem = item;
            if (this.showQrcode) {
                this.createOrder();
            }
        },
        createOrder: function () {
            var self = this;
            self.qrcodeLoading = true;
            let data = new FormData();
            data.append('package_id', self.selectItem.id);
            data.append('platfrom', self.pay);
            data.append('device_id', window._device_id);
            axios.post(_url + '/order/create', data).then(res => {
                //创建成功后 ，轮询查询订单状态
                console.log(res.data)
                self.$message({
                    message: '订单创建成功，请10分钟内扫码支付',
                    type: 'success'
                });
                self.showQrcode = true;
                self.order.orderNo = res.data.orderNum;
                self.order.qrcode = res.data.qrcode;

            }).catch(err => {
                self.$message.error('对不起，服务器遇到点小问题，不能完成操作，请稍后重试。');
            }).finally(__ => {
                self.qrcodeLoading = false;
            });
        },
        queryDialog: function () {
            this.queryDialogVisible = true;
            this.queryDialogLoading = true;
            var self = this;

            let data = new FormData();

            data.append('device_id', window._device_id);
            axios.post(_url + '/order/list', data).then(res => {
                self.queryTableData = res.data;

            }).catch(err => {
                self.$message.error('对不起，服务器遇到点小问题，不能完成操作，请稍后重试。');
            }).finally(__ => {
                self.queryDialogLoading = false;
            });
        }
    }
});
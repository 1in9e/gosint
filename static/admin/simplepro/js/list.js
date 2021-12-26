var crsf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
axios.defaults.transformRequest = [function (data) {

    if (data instanceof FormData) {
        return data;
    }

    data = JSON.parse(JSON.stringify(data))
    data.csrfmiddlewaretoken = crsf_token;
    var params = []
    for (var key in data) {
        var value = data[key];
        if (typeof (value) == "undefined" || String(value) == "") {
            continue
        } else if (typeof (value) == "object") {
            for (var k in value) {
                if (value[k + "__gte"] || value[k + "__lte"]) {
                    delete value[k]
                }
                if (typeof (value[k]) == "undefined" || String(value[k]) == "" || value[k] == null) {
                    delete value[k]
                }
            }
            value = JSON.stringify(value)
            if (value == "{}") {
                continue
            }
        }
        params.push(key + "=" + value);

    }
    return params.join("&");
}];
Date.prototype.format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1,                 //月份
        "d+": this.getDate(),                    //日
        "h+": this.getHours(),                   //小时
        "m+": this.getMinutes(),                 //分
        "s+": this.getSeconds(),                 //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds()             //毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}


function post(params, app, showNotice) {
    app.loading = true;
    if (typeof showNotice == "undefined") {
        showNotice = false;
    }
    return new Promise(((resolve, reject) => {
        axios.post('', params).then(res => {
            if (res.status != 200) {
                //提示网络错误
                app.$notify.error({
                    title: '错误',
                    message: res.statusText
                });
                reject(res);
            } else {
                if (res.data.state) {

                    resolve(res.data.data, res.data);
                    if (showNotice) {

                        if (res.data.messages) {
                            res.data.messages.forEach(item => {
                                setTimeout(function () {
                                    app.$notify({
                                        dangerouslyUseHTMLString: true,
                                        message: item.msg,
                                        type: item.tag
                                    });
                                }, 200)
                            });
                        } else {
                            app.$notify({
                                title: '成功',
                                message: res.data.msg,
                                type: 'success'
                            });
                        }
                    }
                    app.showError = false;
                } else {
                    reject(res.data);
                    app.$notify.error({
                        title: '错误',
                        message: res.data.msg
                    });
                    app.showError = true;
                    app.errorMsg = res.data.msg

                }
            }
        }).catch(function (err) {
            app.$notify.error({
                title: '错误',
                message: err
            });
            app.errorMsg = err;
            app.showError = true;
        }).finally(function () {
            app.loading = false;
            app.search.initialized = true;
            app.$forceUpdate()
        });
    }));
}

var fontConfig = new Vue({
    // el: '#dynamicCss',
    data: {
        fontSize: null
    },
    watch: {
        fontSize: function (newValue) {
            if (newValue != 0) {
                var fontStyle = document.getElementById('fontStyle');
                if (!fontStyle) {
                    fontStyle = document.createElement('style');
                    fontStyle.id = 'fontStyle';
                    fontStyle.type = 'text/css';
                    document.head.append(fontStyle);
                }
                fontStyle.innerHTML = '*{font-size:' + newValue + 'px!important;}'

            } else {
                var fontStyle = document.getElementById('fontStyle');
                if (fontStyle) {
                    fontStyle.remove();
                }
            }
        }
    },
    created: function () {
        var val = getCookie('fontSize');
        if (val) {
            this.fontSize = parseInt(val);
        } else {
            this.fontSize = 0;
        }
    },
    methods: {}
});


new Vue({
    el: '#theme',
    data: {
        theme: '',
    },
    created: function () {
        this.theme = getCookie('theme');

        var self = this;
        //向父组件注册事件
        if (parent.addEvent) {
            parent.addEvent('theme', function (theme) {
                self.theme = theme;
            });

            parent.addEvent('font', function (font) {
                fontConfig.fontSize = font;
            });
        }

    }
})
window.addEventListener('beforeunload', () => {
    if (window.beforeLoad) {
        window.beforeLoad();
    }
});


var app = new Vue({
    el: '#app',
    data: {
        formInline: {},
        layer: {
            visible: false,
            title: '弹出层',
            params: [],
            data: {},
            rules: [],
            action: ''
        },
        form: {
            show: true,
            exportAction: ''
        },
        loading: false,
        errorMsg: null,
        search: {
            current_page: 1,
            action: 'list',
            order_by: null,
            all: 0,
            filters: {},
            search: '',
            page_size: 0,
            initialized: false
        },
        dialog: {
            visible: false,
            title: 'dialog',
            url: null
        },
        toolbars: {
            isActive: true,
            customButtons: [],
            showAll: false
        },
        backupSearch: {},
        exportFormat: 0,
        exts: {},
        table: {
            headers: [],
            rows: [],
            actionFixed: false,
            selection: [],
            summaries: []
        },
        pageSizes: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200],
        paginator: {},
        showError: false,
        cacheKey: ''
    },
    watch: {
        'search.all': function (value) {
            let obj = null;
            for (let key in this.toolbars.customButtons) {
                let temp = this.toolbars.customButtons[key];
                if (temp.isExport) {
                    obj = temp;
                    break;
                }
            }

            if (obj) {
                obj.label = value == 0 ? '导出选中' : '导出全部';
            }
        },
        'table.headers': function (newValue, oldValue) {
            //如果列大于8列，才显示固定列，否则页面布局很诡异
            if (!newValue) {
                return
            }
            if (newValue.length <= 8) {
                this.table.actionFixed = false
            } else {
                this.table.actionFixed = 'right'
            }
        },
        'loading': function (newValue) {
            if (parent.progress) {

                if (newValue) {
                    parent.progress.start();
                } else {
                    parent.progress.done();
                }
            }
        }
    },
    methods: {
        layerDataSubmit(url) {
            const self = this;

            //校验
            for (let key in self.params) {
                let item = self.params[key];
                if (item.require) {
                    if (!item.value || item.value == '' || item.length == 0) {
                        self.$message.error(`"${item.label}" Can't be empty.`)
                        return;
                    }
                }
            }

            //开始提交
            let formData = new FormData();
            //方法名
            formData.append('_action', self.layer.action);
            let selected = [];

            self.table.selection.forEach(item => selected.push(item._id));

            formData.append('_selected', selected.join(','));
            formData.append('select_across', self.search.all);
            //获取选中的数据

            formData.append('csrfmiddlewaretoken', document.querySelector('[name="csrfmiddlewaretoken"]').value);

            for (let key in self.layer.params) {
                let item = self.layer.params[key];
                if (item.type === "file") {
                    formData.append(item.key, this.$refs[item.key][0].files[0]);
                } else if (item.value) {
                    formData.append(item.key, item.value);
                }
            }

            axios.post(url, formData).then(res => {
                if (res.data.status == 'success') {
                    self.layer.visible = false;
                    self.refreshData();
                }
                self.$message({
                    message: res.data.msg,
                    type: res.data.status
                });
            }).catch(err => self.$message.error(err));
        },
        getSummaries: function ({columns, data}) {
            var self = this;
            const sums = [];
            columns.forEach((column, index) => {
                if (self.table.summaries && index < self.table.summaries.length) {
                    sums[index] = self.table.summaries[index];
                    return;
                }
            });


            return sums;
        },
        post: function (params) {
            return post(params, this)
        },
        handleSizeChange: function (val) {
            this.search.page_size = val;
            this.onSubmit();
        },
        onSubmit() {
            var self = this;
            post(self.search, self).then(function (res) {

                //在后续分页数据中不返回该字段，减少网络传输开销
                //headers在当前生命周期内部更新，除非刷新页面
                //self.table.headers.length == 0 &&
                if (res.headers) {
                    res.headers.forEach(item => {
                        item.show = true
                    });
                    self.table.headers = res.headers
                }

                self.table.summaries = res.summaries;

                if (res.exts) {
                    self.exts = res.exts;
                }
                self.table.rows = res.rows
                self.paginator = res.paginator
                if (self.pageSizes.indexOf(res.paginator.page_size) == -1) {
                    self.pageSizes.unshift(res.paginator.page_size);
                }
                self.search.page_size = res.paginator.page_size;
                if (res.custom_button) {
                    self.toolbars.customButtons = res.custom_button
                }

                //调用sdk
                if (window.SIMPLEAPI && window.SIMPLEAPI.loadData) {
                    window.SIMPLEAPI.loadData(self);
                }

                //表格清空
                self.clearSelect();
            });
        },
        pageChange: function (page) {
            this.search.current_page = page;
            this.$nextTick(function () {
                this.onSubmit();
            })
        }, sortChange: function ({column, prop, order}) {
            var mappers = {
                'ascending': '',
                'descending': '-'
            }
            if (!order) {
                this.search.order_by = null;
            } else {
                this.search.order_by = mappers[order] + prop;
            }
            this.$nextTick(function () {
                this.onSubmit();
            });
        },
        refreshData: function () {
            this.search = JSON.parse(JSON.stringify(this.backupSearch));
            this.$nextTick(function () {
                //把储存的数据删掉
                if (sessionStorage) {
                    delete sessionStorage[this.cacheKey];
                }
                this.onSubmit();
                this.toolbars.isActive = true;
            });
        },
        add: function (title) {
            if (window.SIMPLEAPI && window.SIMPLEAPI.toolbar) {
                var rs = window.SIMPLEAPI.toolbar.call({}, 'add', this);
                if (!rs) {
                    return;
                }
            }
            //页内打开
            location.href = location.pathname + 'add';

            //对话框打开
            // this.dialog.url = location.pathname + 'add';
            // this.dialog.title = title;
            // this.dialog.visible = true;
        },
        edit: function (title, id) {

            if (window.SIMPLEAPI && window.SIMPLEAPI.toolbar) {
                var rs = window.SIMPLEAPI.toolbar.call({}, 'edit', this);
                if (!rs) {
                    return;
                }
            }

            if (!id) {
                id = this.table.selection[0]._id
            }
            //页内打开
            location.href = location.pathname + id + '/change/';//页内打开
        },
        dialogClose: function () {
            this.dialog.visible = false;
        },
        selectAll: function (selection, row) {
            this.select(selection, row);
            //显示全部按钮
            this.toolbars.showAll = selection.length != 0;
        },
        select: function (selection, row) {
            this.table.selection = selection;
            this.toolbars.isActive = selection.length <= 0;
        },
        exports: function (btn, key) {
            //设置url
            let url = window.location.href;

            let params = [];
            for (let key in this.search.filters) {
                let value = this.search.filters[key];
                params.push(`${key}=${value}`);
            }

            let paramsString = params.join('&');

            if (url.indexOf('?') == -1) {
                url += '?';
            }
            url += paramsString;
            this.form.exportAction = url;
            document.getElementById('export_form').submit()
        },
        go_url: function (url, icon, name) {
            if (parent.app.openTab) {
                parent.app.openTab({
                    url: url,
                    icon: icon,
                    name: name
                })
            } else {
                window.location.href = url;
            }
        },
        customButtonClick: function (btn, key) {
            const self = this;
            if (window.SIMPLEAPI && window.SIMPLEAPI.toolbar) {
                var rs = window.SIMPLEAPI.toolbar.call(btn, key, this);
                if (!rs) {
                    return;
                }
            }

            //处理layer
            if (btn.layer) {
                self.layer.data = btn.layer;
                self.layer.title = btn.layer.title;
                self.layer.params = btn.layer.params;
                self.layer.action = key;

                self.$nextTick(() => {
                    self.layer.visible = true;
                });

                return;
            }

            //如果是导出按钮，处理导出的数据
            //action: export_admin_action
            // select_across: 0
            // file_format: 0
            // index: 0
            // _selected_action: 15
            if (btn.isExport) {
                return this.exports(btn, key);
            }

            if (btn.confirm) {
                this.$confirm(btn.confirm, '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    done.call(self);
                });
            } else {
                done.call(self);
            }

            function done() {
                if (btn.action_type) {
                    if (!parent.window.app.openTab) {
                        //没有在父框架内打开，就直接跳转
                        btn.action_type = 0;
                    }
                    //打开tab
                    switch (btn.action_type) {
                        case 0:
                            window.location.href = btn.action_url;
                            break;
                        case 1:
                            parent.window.app.openTab({
                                url: btn.action_url,
                                icon: btn.icon || 'fa fa-file',
                                name: btn.short_description,
                                breadcrumbs: []
                            });
                            break;
                        case 2:
                            window.open(btn.action_url)
                            break;
                    }
                } else {

                    //action执行 分为选中某些，和全表选中

                    var all = this.search.all;

                    var data = {
                        action: 'custom_action',
                        all: all,
                        key: key,
                        //自定义的搜索条件
                        filters: this.search.filters
                    }

                    if (all != 1) {
                        var rows = this.table.selection;
                        var ids = []
                        for (i in rows) {
                            ids.push(rows[i]._id);
                        }
                        data['ids'] = ids.join(',');
                    }
                    var self = this;
                    post(data, this, true).then(function (data) {
                        //刷新界面
                        // self.refreshData();
                        self.onSubmit();
                    });
                }
            }


        },
        clearSelect: function () {
            if (this.$refs.table) {
                this.$refs.table.clearSelection();
            }
            this.table.selection = [];
            this.toolbars.showAll = false;
            this.search.all = 0;
            //禁止按钮
            this.toolbars.isActive = true;
        },

        selectAllBtnClick: function () {
            if (this.search.all == 1) {
                this.$refs.table.clearSelection();
                this.table.selection = [];
                this.toolbars.showAll = false;
                this.toolbars.isActive = true;
            } else {
                this.toolbars.isActive = false;
            }
            this.search.all = this.search.all == 0 ? 1 : 0

        },
        changeDate: function (dateList, field, type) {
            if (dateList) {
                if (type == 'date') {
                    this.search.filters[field + '__gte'] = dateList[0].format('yyyy-MM-dd');
                    this.search.filters[field + '__lte'] = dateList[1].format('yyyy-MM-dd');
                } else if (type == 'datetime') {
                    this.search.filters[field + '__gte'] = dateList[0].format('yyyy-MM-dd hh:mm:ss' + window.tz);
                    this.search.filters[field + '__lte'] = dateList[1].format('yyyy-MM-dd hh:mm:ss' + window.tz);
                }
            } else {
                this.search.filters[field + '__gte'] = null;
                this.search.filters[field + '__lte'] = null;
            }
        }, onSearch: function () {
            this.search.current_page = 1;
            this.$nextTick(function () {
                this.onSubmit();
            });
        },
        showDropdown: function (e) {
            //elementui的坑
            var btn = e.target;
            if (btn.tagName == 'BUTTON') {
                //除非i的事件
                btn.getElementsByClassName('el-dropdown-link')[0].click();
            }
        },
        deleteData: function (id) {
            if (window.SIMPLEAPI && window.SIMPLEAPI.toolbar) {
                var rs = window.SIMPLEAPI.toolbar.call({}, 'delete', this);
                if (!rs) {
                    return;
                }
            }
            var self = this;

            var target = self;

            if (parent.app) {
                target = parent.app;
            }
            target.$confirm('此操作将永久删除，是否继续?', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {

                var ids = [];
                if (id) {
                    ids.push(id);
                } else {
                    var rows = self.table.selection;

                    for (var item in rows) {
                        ids.push(rows[item]._id);
                    }
                }

                var ds = {
                    action: 'delete',
                    ids: ids.join(',')
                }

                if (self.search.all == 1) {
                    delete ds['ids'];
                    ds['all'] = 1;
                }

                post(ds, self).then(res => {

                    if (res.state) {
                        self.$notify({
                            title: '成功',
                            message: res.msg,
                            type: 'success'
                        });
                        self.refreshData();

                    } else {
                        app.$notify.error({
                            title: '错误',
                            message: res.msg
                        });
                    }
                }).catch(res => {

                });
            }).catch(() => {

            });
        },
        openDialog: function (title, url) {
            this.dialog.url = url;
            this.dialog.title = title;
            this.dialog.visible = true;
        },
        dbclick: function (row, column, cell, event) {
            var self = this;
            self.dialog.visible = true;
            var url = window.location.href;
            if (url.indexOf('?') == -1) {
                url += "?__=1"
            }
            url += '&_editor=1&_pk=' + row._id
            self.dialog.url = url;

            //给window增加回调事件，保存成功后回调和消息提示
            window.iframe_callback = function (success, msg) {
                if (success) {
                    self.dialog.visible = false;
                    self.$message.success(msg);
                    //对当前页进行刷新
                    self.onSubmit();
                } else {
                    self.$message.error(msg);
                }

            }
        },
        iframeSubmit: function () {
            this.$refs.editorFrame.contentDocument.forms[0].submit();
        },
        //boolean和switch 都会使用element-ui的switch来进行渲染
        //当点击的时候会触发change事件，从而进行ajax请求，更新数据
        booleanChange(pk, field, value, row) {
            post({
                "pk": pk,
                "action": "modify",
                "field": field,
                //将值转成Python可以识别的布尔类型
                "value": value ? "True" : "False"
            }, this, true).catch(err => {
                //设置延时，可以看到修改失败回弹的效果
                setTimeout(() => {
                    row[field] = !value;
                }, 300);
            });
            /*
            步骤：
            1. 拼装数据
            2. 加载loading
            3. 响应和更改，如果失败的话，就改回之前状态
            * */


        }

    },
    mounted: function () {
        //调用sdk
        if (window.SIMPLEAPI && window.SIMPLEAPI.init) {
            window.SIMPLEAPI.init(this);
        }
        if (parent.progress) {
            parent.progress.done();
        }
        if (window.messages) {
            window.messages.forEach(item => {
                setTimeout(function () {
                    app.$notify({
                        dangerouslyUseHTMLString: true,
                        message: item.msg,
                        type: item.tag
                    });
                }, 200)
            });
        }
    },
    created: function () {
        var self = this;

        for (var i in window.seachModels) {
            this.search.filters[window.seachModels[i]] = ''
        }
        this.backupSearch = JSON.parse(JSON.stringify(this.search));
        //用当前页的url来作为key
        this.cacheKey = window._version + '_' + location.pathname;

        this.$nextTick(function () {
            if (sessionStorage) {
                var d = sessionStorage[this.cacheKey]
                if (d) {
                    var data = JSON.parse(d)
                    for (var item in data) {
                        self[item] = data[item];
                    }
                }
            }
            this.onSubmit();
        });

    },
    updated() {
        // console.log('updated')
        //将数据存到sessionStore，下次打开失效
        if (sessionStorage) {
            //克隆
            var clone = JSON.parse(JSON.stringify(this.search));
            //刷新页面的时候，要更新toolbars
            clone.initialized = false;
            sessionStorage[this.cacheKey] = JSON.stringify({
                //只缓存搜索，会减少故障几率
                search: clone
            });
        }
    }
});
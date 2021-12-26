Date.prototype.format = function (formatStr) {
    var str = formatStr;
    var Week = ['日', '一', '二', '三', '四', '五', '六'];

    str = str.replace(/yyyy|YYYY/, this.getFullYear());
    str = str.replace(/yy|YY/, (this.getYear() % 100) > 9 ? (this.getYear() % 100).toString() : '0' + (this.getYear() % 100));

    str = str.replace(/MM/, this.getMonth() > 9 ? (this.getMonth() + 1).toString() : '0' + (this.getMonth() + 1));
    str = str.replace(/M/g, this.getMonth());

    str = str.replace(/w|W/g, Week[this.getDay()]);

    str = str.replace(/dd|DD/, this.getDate() > 9 ? this.getDate().toString() : '0' + this.getDate());
    str = str.replace(/d|D/g, this.getDate());

    str = str.replace(/hh|HH/, this.getHours() > 9 ? this.getHours().toString() : '0' + this.getHours());
    str = str.replace(/h|H/g, this.getHours());
    str = str.replace(/mm/, this.getMinutes() > 9 ? this.getMinutes().toString() : '0' + this.getMinutes());
    str = str.replace(/m/g, this.getMinutes());

    str = str.replace(/ss|SS/, this.getSeconds() > 9 ? this.getSeconds().toString() : '0' + this.getSeconds());
    str = str.replace(/s|S/g, this.getSeconds());

    return str;
}
//网络
Vue.component('m-net', {
    props: ['data'],
    data() {
        return {
            list: [],
            tempRecv: -1,
            tempSent: -1,
            t_recv: 0,
            t_sent: 0
        }
    },
    methods: {
        getValue(val) {
            //kb
            let str = val;
            if (val / 1024 / 1024 >= 1) {
                str = `${parseFloat(val / 1024 / 1024).toFixed(2)}GB`
            } else if (val / 1024 >= 1) {
                str = `${parseFloat(val / 1024).toFixed(2)}MB`
            } else {
                str = `${parseFloat(val).toFixed(2)}KB`
            }
            return str;
        }
    },
    computed: {
        recv() {
            return this.getValue(this.t_recv) + "/s";
        },
        sent() {
            return this.getValue(this.t_sent) + "/s";
        },
        totalRecv() {
            if (!this.data) {
                return "--";
            }
            return this.getValue(this.data.recv)
        },
        totalSent() {
            if (!this.data) {
                return "--";
            }
            return this.getValue(this.data.sent)
        }
    },
    watch: {
        data(value) {
            const self = this;
            let d = new Date().format("HH:mm:ss");


            let recv = value.recv - self.tempRecv;
            let sent = value.sent - self.tempSent;


            if (self.tempSent > -1 && self.tempRecv > -1) {
                self.t_recv = recv;
                self.t_sent = sent;

                this.list.push({
                    date: d,
                    name: '入网',
                    value: recv,
                });

                this.list.push({
                    date: d,
                    name: '出网',
                    value: sent,
                });
                self.plot.changeData(this.list);
            }
            self.tempSent = value.sent;
            self.tempRecv = value.recv;
        }
    },
    template: `
<div>
    <el-row>
        <el-col :span="6">
            <div style="border-left: #f7b851 2px solid;padding-left: 10px;">
                <p>接收</p>
                <p v-text="recv" style="font-size: 12px;color:#666;"></p>
            </div>
        </el-col>
        <el-col :span="6">
         <div style="border-left: rgb(92, 219, 211) 2px solid;padding-left: 10px;">
                <p>发送</p>
                <p v-text="sent" style="font-size: 12px;color:#666;"></p>
            </div>
        </el-col>
        <el-col :span="6">
            <div style="border-left: rgb(255,132,2) 2px solid;padding-left: 10px;">
                <p>总接收</p>
                <p v-text="totalRecv" style="font-size: 12px;color:#666;"></p>
            </div>
        </el-col>
        
          <el-col :span="6">
            <div style="border-left: rgb(26,161,232) 2px solid;padding-left: 10px;">
                <p>总发送</p>
                <p v-text="totalSent" style="font-size: 12px;color:#666;"></p>
            </div>
        </el-col>
    </el-row>
    <div ref="chart" style="height: 300px;"></div>
</div>
    `,
    mounted() {
        const {Line} = G2Plot;
        const line = new Line(this.$refs.chart, {
            data: [],
            padding: 'auto',
            xField: 'date',
            yField: 'value',

            seriesField: 'name',
            yAxis: {
                label: {
                    formatter: (v) => `${(parseFloat(v)).toFixed(2)} Kb/s`,
                },
            },
            legend: {
                position: 'top',
            },
            smooth: true,

            xAxis: {
                tickCount: 5,
            },
            tooltip: {
                formatter: (data) => {
                    return {name: data.name, value: data.value + 'KB/s'};
                }
            }
        });

        line.render();

        this.plot = line;
    }
});

Vue.component('m-cpu', {
    props: ['data'],
    data() {
        return {
            used: 0,
            count: 0
        }
    },
    watch: {
        data(value) {
            this.used = value.used;
            this.count = value.count;
            this.chart.changeData(this.used / 100);
            this.chart.update({
                range: {
                    color: this.getColor(this.used / 100)
                }
            });
        }
    },
    methods: {
        getColor(percent) {
            let color = ['#30BF78', '#FAAD14', '#F4664A'];
            return percent < 0.4 ? color[0] : percent < 0.6 ? color[1] : color[2];
        }
    },
    template: `
   <div>
      
    </div>
    `,
    mounted() {
        const self = this;

        const {Gauge} = G2Plot;
        const gauge = new Gauge(self.$el, {
            percent: self.used,
            range: {
                color: '#30BF78',
            },
            indicator: {
                pointer: {
                    style: {
                        stroke: '#D0D0D0',
                    },
                },
                pin: {
                    style: {
                        stroke: '#D0D0D0',
                    },
                },
            },
            axis: {
                label: {
                    formatter: (v) => {
                        return (v * 100) + '%'
                    }
                }
            },
            statistic: {
                title: {
                    offsetY: -36,
                    style: {
                        fontSize: '14px',
                        color: '#4B535E',
                    },
                    formatter: (v) => {
                        return self.used + '%'
                    },
                },
                content: {
                    style: {
                        fontSize: '20px',
                        lineHeight: '44px',
                    },
                    formatter: () => 'CPU使用率',
                },
            },
        });

        gauge.render();
        this.chart = gauge;
    }
});

Vue.component('m-memory', {
    props: ['data'],
    data() {
        return {
            used: 0,
            total: 0
        }
    },
    watch: {
        data(value) {
            this.used = value.used;
            this.total = value.total;
            this.chart.changeData(value.used / 100);
            this.chart.update({
                range: {
                    color: this.getColor(value.used / 100)
                }
            })
        }
    },
    template: `
   <div>
    </div>
    `,
    mounted() {
        const self = this;

        const {Gauge} = G2Plot;
        const gauge = new Gauge(self.$el, {
            percent: 0,
            range: {
                color: '#30BF78',
            },
            indicator: {
                pointer: {
                    style: {
                        stroke: '#D0D0D0',
                    },
                },
                pin: {
                    style: {
                        stroke: '#D0D0D0',
                    },
                },
            },
            axis: {
                label: {
                    formatter: (v) => {
                        return Math.ceil(v * self.total) + 'GB'
                    }
                }
            },
            statistic: {
                title: {
                    offsetY: -36,
                    style: {
                        fontSize: '14px',
                        color: '#4B535E',
                    },
                    formatter: (v) => {
                        let used = parseFloat((self.used / 100) * self.total).toFixed(2);
                        return `${used}GB/${self.total}GB`
                    },
                },
                content: {
                    style: {
                        fontSize: '20px',
                        lineHeight: '44px',
                        color: '#4B535E',
                    },
                    formatter: () => '内存使用率',
                },
            },
        });

        gauge.render();
        this.chart = gauge;
    },
    methods: {
        getColor(percent) {
            let color = ['#30BF78', '#FAAD14', '#F4664A'];
            return percent < 0.4 ? color[0] : percent < 0.7 ? color[1] : color[2];
        }
    }
});

Vue.component('m-disk', {
    props: ['data'],
    watch: {
        data(value) {
            let temp = [{
                type: '已使用',
                value: value.used / 100
            }, {
                type: '剩余可用',
                value: 1 - (value.used / 100)
            }]
            this.chart.changeData(temp);
        }
    },
    template: `
   <div ref="chart"></div>
    `,
    mounted() {
        const self = this;

        const {Pie} = G2Plot;
        const pie = new Pie(self.$el, {
            appendPadding: 10,
            data: [],
            angleField: 'value',
            colorField: 'type',
            radius: 0.9,
            label: {
                type: 'inner',
                offset: '-30%',
                content: ({percent}) => `${(percent * 100).toFixed(0)}%`,
                style: {
                    fontSize: 14,
                    textAlign: 'center',
                },
            },
            interactions: [{type: 'element-active'}],
        });
        pie.render();
        this.chart = pie;
    }
});
//监控模块
Vue.component('monitor', {
    props: ['url'],
    data() {
        return {
            data: {},
            isActive: true,
            loading: true
        }
    },
    created() {
        const self = this;

        //浏览器失去焦点就停止查询，节省开销
        window.addEventListener('focus', e => {
            self.isActive = true;
        });

        window.addEventListener('blur', e => {
            self.isActive = false;
        });

        setInterval(() => {
            if (!self.isActive) {
                return;
            }

            //标签页没选中，也不更新图表
            if (!app || app.tabModel !== '0') {
                return;
            }

            let formData = new FormData();
            formData.append('csrfmiddlewaretoken', document.querySelector('[name="csrfmiddlewaretoken"]').value);
            axios.post(self.url, formData).then(res => {
                self.data = res.data;
            }).catch(err => self.$message.error(err))
                .finally(_ => self.loading = false);
        }, 2000);
    },
    template: `
    <div>
        <el-row v-loading="loading">
            <el-col :span="24">
                <m-net :data="data.net"></m-net>
            </el-col>
            </el-row>
        <el-divider content-position="left"></el-divider>
         <el-row>   
            <el-col :span="12" style="padding:0px 30px;">
                <m-cpu :data="data.cpu"></m-cpu>
            </el-col>
            <el-col :span="12" style="padding:0px 30px;">
                <m-memory :data="data.memory"></m-memory>
            </el-col>
        </el-row>
    </div>
    `
});
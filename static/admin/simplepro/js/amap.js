Vue.component('amap', {
    props: ['value', 'apiKey', 'pickType'],
    data() {
        let pos = [114.059683, 22.543615];
        if (this.$attrs.picktype === 'geo') {
            pos = this.value.split(',')
        }
        return {
            id: "amap_callback_" + (Math.random() + "").replace(/\./g, ''),
            dialogVisible: false,
            loading: true,
            pos: pos
        }
    },
    mounted() {
        let self = this;
        //引入js
        let elId = 'amap_js';
        if (!document.querySelector('#' + elId)) {
            let src = `https://webapi.amap.com/maps?v=1.4.15&key=${self.$attrs.apikey}`;
            var jsapi = document.createElement('script');
            jsapi.src = src;
            jsapi.setAttribute('id', elId);
            document.head.appendChild(jsapi);
        }
    },
    methods: {
        addMarker() {

            let self = this;
            console.log(self.pos)
            let marker = new AMap.Marker({
                map: this.map,

                icon: new AMap.Icon({
                    image: "https://webapi.amap.com/theme/v1.3/markers/n/mark_bs.png",
                    size: new AMap.Size(58, 30),
                    imageOffset: new AMap.Pixel(-0, -0)
                }),
                position: self.pos,
                offset: new AMap.Pixel(-5, -30),
                draggable: false
            });

            // marker.on('dragend', () => {
            //     console.log(marker.getPosition())
            //     let pos = marker.getPosition();
            //     self.setValue([pos.lng, pos.lat]);
            // });

            this.marker = marker;
        },

        initGeoPlugin() {
            let self = this;
            this.map.plugin(["AMap.Geocoder"], function () {
                self.geocoder = new AMap.Geocoder({
                    radius: 1000,
                    extensions: "all"
                });

                //判断如果是address，就获取经纬度
                if (self.$attrs.picktype === 'address') {
                    self.geocoder.getLocation(self.value, (status, result) => {
                        let geocodes = result.geocodes;
                        if (geocodes.length > 0) {
                            self.marker.setPosition(geocodes[0].location);
                        }
                        self.loading = false;
                    });
                }
            });

        },
        showMap() {
            let self = this;
            self.dialogVisible = true;
            self.$nextTick(() => {
                self.map = new AMap.Map(self.id, {
                    center: self.pos,
                    zoom: 11
                });
                self.map.on('complete', () => {
                    self.addMarker();

                    if(self.$attrs.picktype==='geo'){
                        self.loading = false;
                    }

                    self.initGeoPlugin();
                })

                self.map.plugin(['AMap.ToolBar', 'AMap.Scale', 'AMap.OverView', 'AMap.MapType', 'AMap.Geolocation'], () => {
                    self.map.addControl(new AMap.ToolBar());
                    self.map.addControl(new AMap.Scale());
                });
            })

        }
    },
    template: `<div>
    <a href="javascript:void(0)" @click="showMap()" v-text="value"></a>
    <el-dialog
      title="坐标查看"
      :visible.sync="dialogVisible"
      width="50%">
      <el-alert type="success" style="margin-bottom: 10px;">坐标值：<span v-text="value"></span></el-alert>
      <div :id="id" style="height:50%" v-loading="loading">地图容器</div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false">确 定</el-button>
      </span>
    </el-dialog>
</div>`
});
Vue.component('s-dialog', {
    props: ['url', 'title', 'show'],
    template: '<el-dialog width="80%" @closed="closed" :title="title" :visible.sync="visible"><iframe :src="url" frameborder="0" height="100%" width="100%"></iframe></el-dialog>',
    data() {
        return {
            visible: this.show
        }
    },
    watch:{
      show:function (newValue) {
          this.visible = newValue;
      }
    },
    methods: {
        closed() {
            this.$emit('close');
        }
    }
});
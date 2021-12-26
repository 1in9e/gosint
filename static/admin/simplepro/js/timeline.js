Vue.component('timeline', {
    props: ['show'],
    data: function () {
        return {}
    },
    created: function () {

    },
    mounted: function () {
    },
    template: '#timeline'
});

Vue.component('timeline-btn', {
    data: function () {
        return {
            show: false
        }
    },
    methods: {
        click: function () {
            this.show = !this.show;
        }
    },
    template: '<span @click="click" circle><slot></slot><timeline :show="show"></timeline></span>'
});
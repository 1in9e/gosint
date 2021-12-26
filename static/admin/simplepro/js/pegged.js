/**
 * Vue+Element-UI来渲染默认select
 * Website: https://simpleui.88cto.com
 * */

class Pegged {
    auto(types) {
        for (var field in types) {
            var el = document.querySelector(`*[name="${field}"]`);
            if (el) {
                var type = types[field];
                switch (type) {
                    case 'select':
                        this.registerSelect(el)
                        break
                    case 'boolean':
                        this.registerBoolean(el);
                        break
                }
            }
        }
    }


    registerBoolean(el) {
        var id = '_boolean_' + new Date().getTime();
        if (!el.insertAdjacentHTML) {
            return;
        }

        el.insertAdjacentHTML('afterend', `
            <div id="${id}" :style="style">
<!--                <input type="hidden" :name="name" :checked="value=='on'">-->
                <el-switch :name="name"
                    active-value="on"
                    inactive-value="off"
                  v-model="value">
                </el-switch>
            </div>
        `);

        new Vue({
            el: '#' + id,
            data: {
                value: '',
                name: '',
                style: {}
            },
            created() {
                var self = this;
                var fiedls = ['display', 'float', 'width'];
                fiedls.forEach(f => {
                    self.style[f] = el.style[f];
                });
                if (!self.style.display || self.style.display == '') {
                    self.style.display = 'inline-block';
                }
                el.style.display = 'none';
                this.value = el.checked ? 'on' : 'off';
                this.name = el.name;
                //移除name，防止表单提交
                el.removeAttribute('name');
            }
        });
    }

    hasClass(el, className) {
        var exists = false;
        if (!el.classList) {
            return exists;
        }
        for (var i = 0; i < el.classList.length; i++) {
            if (el.classList[i] == className) {
                exists = true;
                break;
            }
        }
        return exists;
    }

    registerSelect(el, size) {
        if (document.querySelectorAll(".inline-related").length != 0) {
            return;
        }
        //如果有多选属性，不处理
        if (el && el.hasAttribute && el.hasAttribute('multiple')) {
            return;
        }
        if (this.hasClass(el, 'admin-autocomplete')) {
            return;
        }

        //在el相邻位置增加一个Vue组件
        var id = '_select_' + new Date().getTime();
        if (!el.insertAdjacentHTML) {
            return;
        }

        el.insertAdjacentHTML('afterend', `
                    <div id="${id}" :style="style">
                        <input type="hidden" :name="name" v-model="value">
                        <el-select :size="s" v-model="value" filterable clearable>
                            <el-option
                              v-for="item in options"
                              :key="item.value"
                              :label="item.label"
                              :value="item.value">
                            </el-option>
                          </el-select>
                      </div>
        `);
        new Vue({
            el: '#' + id,
            data: {
                value: '',
                name: '',
                options: el.options,
                style: {},
                s: ''
            },
            created() {
                var self = this;
                var fiedls = ['display', 'float', 'width'];
                fiedls.forEach(f => {
                    self.style[f] = el.style[f];
                });
                if (!self.style.display || self.style.display == '') {
                    self.style.display = 'inline-block';
                }
                el.style.display = 'none';
                this.value = el.value;
                this.name = el.name;
                //移除name，防止表单提交
                el.removeAttribute('name');
                self.s = size;
            }
        });

    }
}

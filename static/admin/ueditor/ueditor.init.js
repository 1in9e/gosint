window.onload = function () {
    if (window.ueditors) {
        window.ueditors.forEach(id => {
            UE.getEditor(id)
        });
    }
}

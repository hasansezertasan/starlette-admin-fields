(function () {
    function processCustomElement(element) {
        // CKEditor4Field integration
        $(".field-ckeditor4", element).each(function () {
            let options = $(this).data("options");
            CKEDITOR.replace(this, options);
        });
        // end CKEditor4Field integration

        // CKEditor5Field integration
        $(".field-ckeditor5", element).each(function () {
            ClassicEditor
                .create(
                    this,
                )
                .catch(error => {
                    console.error(error);
                });
        });
        // end CKEditor5Field integration

        // SimpleMDEField integration
        $(".field-simplemde", element).each(function () {
            let options = $(this).data("options");
            new SimpleMDE({
                element: this,
                ...options
            });
        });
        // end SimpleMDEField integration

    }
    $(function () {
        processCustomElement(document);
    });
})();

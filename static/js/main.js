/* =====================================================
   RICELEAFXNET COMMON JAVASCRIPT
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* -------------------------------------------------
           ALWAYS HIDE LOADER WHEN PAGE IS READY
        ------------------------------------------------- */

        const loader =
            document.getElementById("loader");

        if (loader) {

            loader.classList.remove(
                "active"
            );

            loader.style.display =
                "none";
        }


        /* -------------------------------------------------
           UPLOAD ELEMENTS
        ------------------------------------------------- */

        const uploadArea =
            document.getElementById(
                "uploadArea"
            );

        const fileInput =
            document.getElementById(
                "fileInput"
            );

        const preview =
            document.getElementById(
                "preview"
            );


        /* -------------------------------------------------
           EMPTY PREVIEW ELEMENT
        ------------------------------------------------- */

        const emptyPreview =
            document.getElementById(
                "emptyPreview"
            );


        /* -------------------------------------------------
           UPLOAD AREA
        ------------------------------------------------- */

        if (
            uploadArea &&
            fileInput
        ) {

            /* ---------------------------------------------
               CLICK UPLOAD AREA
            --------------------------------------------- */

            uploadArea.addEventListener(
                "click",
                function () {

                    fileInput.click();

                }
            );


            /* ---------------------------------------------
               FILE SELECTION
            --------------------------------------------- */

            fileInput.addEventListener(
                "change",
                function () {

                    if (
                        this.files &&
                        this.files.length > 0
                    ) {

                        showPreview(
                            this.files[0]
                        );

                    }

                }
            );


            /* ---------------------------------------------
               DRAG OVER
            --------------------------------------------- */

            uploadArea.addEventListener(
                "dragover",
                function (event) {

                    event.preventDefault();

                    uploadArea.classList.add(
                        "dragover"
                    );

                }
            );


            /* ---------------------------------------------
               DRAG LEAVE
            --------------------------------------------- */

            uploadArea.addEventListener(
                "dragleave",
                function () {

                    uploadArea.classList.remove(
                        "dragover"
                    );

                }
            );


            /* ---------------------------------------------
               DROP
            --------------------------------------------- */

            uploadArea.addEventListener(
                "drop",
                function (event) {

                    event.preventDefault();

                    uploadArea.classList.remove(
                        "dragover"
                    );


                    const files =
                        event.dataTransfer.files;


                    if (
                        files &&
                        files.length > 0
                    ) {

                        try {

                            fileInput.files =
                                files;

                        }
                        catch (error) {

                            console.log(
                                "File assignment:",
                                error
                            );

                        }


                        showPreview(
                            files[0]
                        );

                    }

                }
            );

        }



        /* -------------------------------------------------
           PREVIEW FUNCTION
        ------------------------------------------------- */

        function showPreview(file) {

            if (
                !preview ||
                !file
            ) {

                return;

            }


            /* ---------------------------------------------
               IMAGE TYPE VALIDATION
            --------------------------------------------- */

            if (
                !file.type.startsWith(
                    "image/"
                )
            ) {

                alert(
                    "Please select an image file."
                );

                return;

            }


            /* ---------------------------------------------
               FILE READER
            --------------------------------------------- */

            const reader =
                new FileReader();


            reader.onload =
                function (event) {


                    /* -------------------------------------
                       SHOW IMAGE
                    ------------------------------------- */

                    preview.src =
                        event.target.result;

                    preview.style.display =
                        "block";


                    /* -------------------------------------
                       HIDE EMPTY PREVIEW MESSAGE
                    ------------------------------------- */

                    if (emptyPreview) {

                        emptyPreview.style.display =
                            "none";

                    }

                };


            reader.readAsDataURL(
                file
            );

        }



        /* -------------------------------------------------
           FORM LOADER
        ------------------------------------------------- */

        const scanForm =
            document.getElementById(
                "scanForm"
            );


        if (scanForm) {

            scanForm.addEventListener(
                "submit",
                function (event) {


                    /* -------------------------------------
                       CHECK FILE
                    ------------------------------------- */

                    if (
                        !fileInput ||
                        !fileInput.files ||
                        fileInput.files.length === 0
                    ) {

                        event.preventDefault();


                        alert(
                            "Please select a rice leaf image."
                        );


                        return;

                    }


                    /* -------------------------------------
                       SHOW ANALYSIS LOADER
                    ------------------------------------- */

                    showLoader();

                }
            );

        }



        /* -------------------------------------------------
           BROWSER BACK / FORWARD FIX
        ------------------------------------------------- */

        window.addEventListener(
            "pageshow",
            function () {

                if (loader) {

                    loader.classList.remove(
                        "active"
                    );

                    loader.style.display =
                        "none";

                }

            }
        );



        /* -------------------------------------------------
           SHOW LOADER
        ------------------------------------------------- */

        function showLoader() {

            if (!loader) {

                return;

            }


            loader.classList.add(
                "active"
            );


            loader.style.display =
                "flex";

        }



        /* -------------------------------------------------
           HIDE LOADER
           Useful after returning to the page
        ------------------------------------------------- */

        function hideLoader() {

            if (!loader) {

                return;

            }


            loader.classList.remove(
                "active"
            );


            loader.style.display =
                "none";

        }



        /* -------------------------------------------------
           INITIAL LOADER RESET
        ------------------------------------------------- */

        hideLoader();

    }
);
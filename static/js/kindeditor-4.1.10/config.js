KindEditor.ready(function(K) {
    K.create('#id_content',{
                    width:'100%',
                    height:'300px',
                    uploadJson: '/admin/upload/kindeditor',
                    afterBlur: function () {
                        this.sync();   // 同步KindEditor的值到textarea文本框
                    }
                });

    K.create('#article_content',{
                    width:'100%',
                    height:'300px',
                    uploadJson: '/admin/upload/kindeditor',
                    afterBlur: function () {
                        this.sync();   // 同步KindEditor的值到textarea文本框
                    }
                });

    K.create('#comment',{
                    width:'100%',
                    height:'200px',
                    uploadJson: '/admin/upload/kindeditor',
                    afterBlur: function () {
                        this.sync();   // 同步KindEditor的值到textarea文本框
                    }
                });

               // prettyPrint();

        });


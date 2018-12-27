function createEmbedVideoChooser(id) {
    var chooserElement = $('#' + id + '-chooser');
    var previewEmbedVideo = chooserElement.find('.preview-image img');
    var input = $('#' + id);
    var editLink = chooserElement.find('.edit-link');

    $('.action-choose', chooserElement).click(function() {
        ModalWorkflow({
            'url': window.chooserUrls.embedVideoChooser,
            'onload': EMBED_VIDEO_CHOOSER_MODAL_ONLOAD_HANDLERS,
            'responses': {
                'embedVideoChosen': function(embedVideoData) {
                    if (typeof embedVideoData == 'string') {
                        embedVideoData = JSON.parse(embedVideoData);
                    }
                    input.val(embedVideoData.id);
                    previewEmbedVideo.attr({
                        'src': embedVideoData.preview.url,
                        'alt': embedVideoData.title
                    });
                    chooserElement.removeClass('blank');
                    editLink.attr('href', embedVideoData.edit_link);
                }
            }
        });
    });

    $('.action-clear', chooserElement).click(function() {
        input.val('');
        chooserElement.addClass('blank');
    });
}

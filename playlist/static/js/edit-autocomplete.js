var trackCount = 0;
var localCount = 0;
var ausCount = 0;
var femaleCount = 0;

var artists = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/api/artists/?format=json&term=%QUERY',
    wildcard: '%QUERY',
    rateLimitBy: 100,
  }
});

var tracks = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/api/tracks/?format=json&track=%QUERY',
    wildcard: '%QUERY',
    rateLimitBy: 100,
    transform: function(result) {
        return result.results;
    }
  }
});


$('.typeahead-artist').each(function() {
    $(this).typeahead(null, {
        name: 'artists',
        source: artists,
        limit: 10,
});
});

function updateQuotas() {
    localRatio = localCount / (trackCount * 0.2);
    ausRatio = ausCount / (trackCount * 0.4);
    femaleRatio = femaleCount / (trackCount * 0.25);

    $('#local_quota').html("" + localCount + "/" + (trackCount * 0.2).toFixed( 0));
    $('#aus_quota').html("" + ausCount + "/" + (trackCount * 0.4).toFixed( 0));
    $('#female_quota').html("" + femaleCount + "/" + (trackCount * 0.25).toFixed( 0));

    if (trackCount < 3) {
        $('#local_label').switchClass("label-warning label-danger label-success", "label-default");
    }
    else if (localRatio >= 1) {
        $('#local_label').switchClass("label-warning label-danger", "label-success");
    }
    else if (localRatio >= 0.7) {
        $('#local_label').switchClass("label-success label-danger", "label-warning");
     }
    else  {
        $('#local_label').switchClass("label-success label-warning", "label-danger");
    }

    if (trackCount < 2) {
        $('#aus_label').switchClass("label-warning label-danger label-success", "label-default");
    }
    else if (ausRatio >= 1) {
        $('#aus_label').switchClass("label-warning label-danger", "label-success");
    }
    else if (ausRatio >= 0.7) {
        $('#aus_label').switchClass("label-success label-danger", "label-warning");
     }
    else  {
        $('#aus_label').switchClass("label-success label-warning", "label-danger");
    }

    if (trackCount < 2) {
        $('#aus_label').switchClass("label-warning label-danger label-success", "label-default");
    }
    else if (femaleRatio >= 1) {
        $('#female_label').switchClass("label-warning label-danger", "label-success");
    }
    else if (femaleRatio >= 0.7) {
        $('#female_label').switchClass("label-success label-danger", "label-warning");
     }
    else  {
        $('#female_label').switchClass("label-success label-warning", "label-danger");
    }
}

function updatePlayCount() {
    trackCount = 0;
    $('.typeahead-track').each(function() {
        if ($(this).val() == "") {

        }
        else {
            trackCount++;
        }
    });
    updateQuotas();
}

$('.typeahead-track').each(function() {
    if ($(this).val() == "") {

    }
    else {
        trackCount++;
    }
    console.log($(this)[0].id);
    $(this).on('input', function() {
        updatePlayCount();
        });
    $(this).typeahead(null, {
        name: 'tracks',
        source: tracks ,
        display: function(suggestion) {
            return suggestion.tracktitle;
        }
});
});

$('.local_check').each(function() {
    if ($(this).is(':checked'))
        localCount++;
    $(this).click(function() {
        if ($(this).is(':checked'))
            localCount++;
        else
            localCount--;
        updateQuotas();
    });
    updateQuotas();
});

$('.australian_check').each(function() {
    if ($(this).is(':checked'))
        ausCount++;
    $(this).click(function() {
        if ($(this).is(':checked'))
            ausCount++;
        else
            ausCount--;
        updateQuotas();
    });
    updateQuotas();
});

$('.female_check').each(function() {
    if ($(this).is(':checked'))
        femaleCount++;
    $(this).click(function() {
        if ($(this).is(':checked'))
            femaleCount++;
        else
            femaleCount--;
        updateQuotas();
    });
    updateQuotas();
});





// Prevent return key from submitting form
$(document).ready(function() {
  $(window).keydown(function(event){
    if(event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
});


$('.floathead').floatThead({
    position: 'fixed'
});

jQuery(document).ready(function($){
    
    alert('Los datos que introduzcas serán registrados como parte del experimento.\n No envies datos personales o contraseñas');
    /* Store the url shown */
    var current_url_shown = "" // this is used to avoid continous recharging of the web
    
    /* Vademecum base url */
    var vademecum_base = "http://www.dit.upm.es/~pepe/libros/vademecum/index.html?n="
   
    // Creates (or loads from cookie) a random user id for the bot
    var username = "";
    if(document.cookie && document.cookie.indexOf("botUser") != -1) {
       data = document.cookie.split(";");
       for (var i = 0; i < data.length; i++) {
           cookie = data[i].trim();
           //console.log(document.cookie);
           if (cookie.indexOf("botUser") == 0) {
               username = cookie.substr("botUser=".length, cookie.length -1);
            }
       }
    } else {
       username = randomString(5);
       document.cookie = "botUser="+username+";";
    };
    
    // First time answer, send a question to get the gambit response
    json_data = {'username': username, 'question':'Hola'};
    $.ajax({ url: $('#ask-form').attr('action'),
             data: json_data,
             dataType: 'json',
             contentType: 'application/json;charset=UTF-8',
             success: populateForm,
             error: function(data_resp) {
                 alert("Esto es un error");
                 console.log("Error connection to the controller");
             }
    });

    /** Hide/show effect */
    $('#bot_chat_window #upper_bar a#max_icon').click(function(){
        $('#bot_chat_window').toggleClass('visible');
        $('#bot_chat_window #screen_wrapper form input[name=question]').val('');
        $('#bot_chat_window #screen_wrapper form input[name=question]').focus();
        return false;
    });
    
    /** Request questionnaire */
    $('#bot_chat_window #upper_bar a#quiz').click(function(){
        $('#bot_chat_window #screen_wrapper form input[name=question]').val('Quiero rellenar la encuesta de satisfacción');
        return false;
    });

    // Set the username in the span    
    $('#username').html(username);
    
    $('#ask-form').on('submit', function() {
        var form = $(this);
        var form_data = form.serializeArray();
        var input_field = form.children('input[name=question]');

        if (form[0].value == '') {
            //TODO: Add an alert to say there needs to be data
            return false;
        };
        
        var json_data = {};
        $.map(form_data, function(n, i){
            json_data[n['name']] = n['value'];
        });
        
        json_data.username = username;
        
        // Add the question 
        $('#screen').append(constructDialogEntry('Me', json_data.question));
        scrollDisplay();
        input_field.val('')
        $.ajax({ url: form.attr('action'),
                 data: json_data,
                 dataType: 'json',
                 contentType: 'application/json;charset=UTF-8',
                 success: populateForm,
                 error: function(data_resp) {
                        $('#screen').append(constructDialogEntry('Duke',
                                'Vaya, parece que he tenido alg|ú|n error conectando con el servidor... Whoops'));
                        console.log("Error connection to the controller");
                    return false;
                 }
        });
        return false;
    });
    
    function populateForm (data_resp) {
        console.log(data_resp);
        if (data_resp.answer) { 
            data_resp.answer.forEach(function(answer) {
                $('#screen').append(constructDialogEntry('Duke', answer));
		scrollDisplay();
                if (data_resp.resource) {
                    if (data_resp.resource.indexOf('vademecum') != -1 ){
                        // This links to the vademecum
                        var name_start = data_resp.resource.lastIndexOf('/')+1
                        var filename = data_resp.resource.substring(name_start)
                        $('#iframe-qa').attr('src', vademecum_base + filename);
                        current_url_shown = vademecum_base + filename;
                    } else {
                        //I have some other link
                        $('#iframe-qa').attr('src', data_resp.resource);
                        current_url_shown = data_resp.resource;
                    }
                }
            });
        } else {
            $('#screen').append(constructDialogEntry('Duke',
                                'Lo siento, no puedo responder a esa pregunta'));
	    scrollDisplay();
        }
        scrollDisplay();
    }
    // Generates a Random string for the user id
    function randomString(length) {
        charSet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var result = '';
        for (var i = length; i > 0; --i) result += charSet[Math.round(Math.random() * (charSet.length - 1))];
        return result;
    }
    
         /* This scrolls the display to the bottom, just to show all the messages.
     * It can be overriden to use a different animation */
    function scrollDisplay () {
        // Nice scroll to last message
        $("#screen").scrollTo('100%', 0);  
    }
    
    /* This construct html formatted dialog entry */
    function constructDialogEntry (nick, entry) {
        return '<div class="dia_entry">\
                  <span class="nick">' + nick + ':</span>\
                  <span class="text">' + entry + '</span>\
                </div>'
    };
    
});

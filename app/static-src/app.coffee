# wrap timeout
wait = (ms, f) -> setTimeout(f, ms)

# show tags after clicking ellipsis
$('a.js-show-tags').live 'click', ->
    $(@).parent().hide().next().fadeIn(300)
    off

# autohide tags
$('.js-tags').live 'hover', (ev) ->
    $elem = $(@)
    if ev.type is 'mouseenter'
        $elem.data(lock: on)
    else
        $elem.data(lock: off)
        wait 4000, ->
            if not $elem.data('lock')
                $elem.fadeOut(300).prev().delay(300).fadeIn(300)

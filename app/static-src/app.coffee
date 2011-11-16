# wrap timeout
wait = (ms, f) -> setTimeout(f, ms)

# use pjax
$('a.js-pjax').pjax('#content').live 'click', (ev) ->
    # quit, if it's not a normal click
    return true if ev.which != 1 or ev.metaKey or ev.shiftKey

    # fade out
    $('div, h1, table', '#content').fadeOut(300)

    # scroll to top (do this weird trick with oneoff callback to make
    # browsers' "back" button respect scroll)
    $('body').one 'pjax:end', ->
        scrollTo(0, 0)

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

# hide nav
$ ->
    timeFor = (i) -> 2500 + 300 * i

    $nav = $('#nav')
    $elems = $('a, span', $nav)

    $elems.each (i, elem) ->
        wait timeFor(i), ->
            $(elem).addClass('ninja')

    wait timeFor($elems.length) + 1000, ->
        $nav.addClass('ninja').find('a, span').each ->
            $(@).removeClass('ninja')

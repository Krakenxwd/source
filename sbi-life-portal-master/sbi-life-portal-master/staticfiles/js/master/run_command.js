/* global console */
/* global $ */
/* jshint esversion: 6 */

let thisScript = document.currentScript;

$(document).ready(function () {
    let commands = JSON.parse(thisScript.getAttribute('commands'));
    let commandKeys = Object.keys(commands);
    let $application = $('#application');
    let $command = $('#command');
    var parsed_data = {};

    $application.select2({
        'placeholder': 'Select Application',
    });

    $command.select2({
        'placeholder': 'Select Command',
    });

    function appendOptions($element, dataArray, option_array, id_to_check = null) {
        dataArray.forEach(function (data) {
            if ($.inArray(String(data['id']), option_array) == -1) {
                if (id_to_check) {
                    if (id_to_check != data['id'].slice(0, 3)) {
                        return
                    }
                }
                newOption = new Option(data['value'], data['id'], true, false);
                $element.append(newOption).trigger('change');
            }
        });

    }

    $application.on('select2:selecting', function (e) {
        let appName = e.params.args.data.text
        $command.find('option').remove()
        if (appName) {
            $.each(commands, function (key, value) {
                if (appName == value) {
                    newOption = new Option(key, key, true, false);
                    $command.append(newOption).trigger('change');
                }
            });
        }
    })

});
/* global console */
/* global $ */
/* jshint esversion: 6 */

let $analyzeSubmitBtn = $('#analyze-submit-btn');
let $reportrange = $('#reportrange');
let $exportReportrange = $('#export-reportrange');

$analyzeSubmitBtn.on('click', function () {
    let daterange = $reportrange.val();
    $exportReportrange.val(daterange);
});


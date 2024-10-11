/* global Chart */

const elementBody = document.querySelector('body');
const elementBodyCss = getComputedStyle(elementBody);

Chart.defaults.color = elementBodyCss.color;

/**
 * Draw a chart on the given element with the given data and options using Chart.js
 *
 * @param {HTMLElement} element The element to draw the chart on
 * @param {string} chartType The type of chart to draw
 * @param {object} data The data to draw
 * @param {object} options The options to draw the chart with
 */
const drawChart = (element, chartType, data, options) => { // eslint-disable-line no-unused-vars
    'use strict';

    const chart = new Chart(element, { // eslint-disable-line no-unused-vars
        type: chartType,
        data: data,
        options: options
    });
};

$(document).ready(() => {
    'use strict';

    const btnMainCharacterDetails = $('.btn-afat-corp-stats-view-character');

    if (btnMainCharacterDetails.length > 0) {
        btnMainCharacterDetails.on('click', (event) => {
            const btn = $(event.currentTarget);
            const characterId = btn.data('character-id');
            const characterName = btn.data('character-name');

            console.log(btn);
            console.log(characterId);

            $('#col-character-alt-characters').removeClass('d-none');
            $('#afat-corp-stats-main-character-name').text(characterName);
        });
    }
});

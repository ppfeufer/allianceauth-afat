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

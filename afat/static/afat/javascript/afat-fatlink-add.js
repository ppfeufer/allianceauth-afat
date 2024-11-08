import Autocomplete from '/static/afat/libs/bootstrap5-autocomplete/1.1.25/autocomplete.min.js';

$(document).ready(() => {
    'use strict';

    /**
     * Initialize autocomplete dropdown
     *
     * @param {HTMLElement} element
     */
    const autoCompleteDropdown = (element) => {
        const datalistId = element.getAttribute('data-datalist');
        const datalist = document.getElementById(datalistId);

        if (datalist) {
            const autoCompleteDoctrine = new Autocomplete( // eslint-disable-line no-unused-vars
                element,
                Object.assign(
                    {},
                    {
                        onSelectItem: console.log,
                    },
                    {
                        onRenderItem: (item, label) => {
                            return `<l-i set="fl" name="${item.value.toLowerCase()}" size="16"></l-i> ${label}`;
                        },
                    }
                )
            );
        }
    };

    autoCompleteDropdown(document.getElementById('id_doctrine_esi'));
    autoCompleteDropdown(document.getElementById('id_doctrine'));
});

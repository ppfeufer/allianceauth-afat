/* global afatSettings, characters, moment, manageModal, AFAT_DATETIME_FORMAT, fetchGet */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;

    /**
     * DataTable :: Recent FATs per character
     */
    if (characters.length > 0) {
        characters.forEach((character) => {
            const recentFatsCharacterTable = $('#recent-fats-character-' + character.charId);
            const url = afatSettings.url.characterFats.replace('0', character.charId);

            fetchGet({url: url})
                .then((data) => {
                    recentFatsCharacterTable.DataTable({
                        language: dtLanguage,
                        data: data,
                        columns: [
                            {data: 'fleet_name'},
                            {data: 'fleet_type'},
                            {data: 'doctrine'},
                            {data: 'system'},
                            {data: 'ship_type'},
                            {
                                data: 'fleet_time',
                                render: {
                                    /**
                                     * Render date
                                     *
                                     * @param data
                                     * @returns {*}
                                     */
                                    display: (data) => {
                                        return moment(data.time).utc().format(
                                            AFAT_DATETIME_FORMAT
                                        );
                                    },
                                    _: 'timestamp'
                                }
                            }
                        ],
                        paging: false,
                        ordering: false,
                        searching: false,
                        info: false
                    });
                })
                .catch((error) => {
                    console.error('Error fetching recent FATs for character:', character.charId, error);
                });
        });
    }

    /**
     * DataTable :: Recent FAT links
     */
    const noFatlinksWarning = '<div class="aa-callout aa-callout-warning" role="alert">' +
        '<p>' + afatSettings.translation.dataTable.noFatlinksWarning + '</p>' +
        '</div>';

    const recentFatlinksTableColumns = [
        {data: 'fleet_name'},
        {data: 'fleet_type'},
        {data: 'doctrine'},
        {data: 'creator_name'},
        {
            data: 'fleet_time',
            render: {
                /**
                 * Render timestamp
                 *
                 * @param data
                 * @returns {*}
                 */
                display: (data) => {
                    return moment(data.time).utc().format(AFAT_DATETIME_FORMAT);
                },
                _: 'timestamp'
            }
        }
    ];

    const recentFatlinksTableColumnDefs = [];

    if (afatSettings.permissions.addFatLink === true || afatSettings.permissions.manageAfat === true) {
        recentFatlinksTableColumns.push({
            data: 'actions',
            /**
             * Render action buttons
             *
             * @param data
             * @returns {*|string}
             */
            render: (data) => {
                return data;
            }
        });

        recentFatlinksTableColumnDefs.push({
            targets: [5],
            orderable: false,
            createdCell: (td) => {
                $(td).addClass('text-end');
            }
        });
    }

    dtLanguage.emptyTable = noFatlinksWarning;

    fetchGet({url: afatSettings.url.recentFatLinks})
        .then((data) => {
            $('#dashboard-recent-fatlinks').DataTable({
                language: dtLanguage,
                data: data,
                columns: recentFatlinksTableColumns,
                columnDefs: recentFatlinksTableColumnDefs,
                paging: false,
                ordering: false,
                searching: false,
                info: false
            });
        })
        .catch((error) => {
            console.error('Error fetching recent FAT links:', error);
        });

    /**
     * Modal :: Close ESI fleet
     */
    const cancelEsiFleetModal = $(afatSettings.modal.cancelEsiFleetModal.element);
    manageModal(cancelEsiFleetModal);

    /**
     * Modal :: Delete FAT link
     */
    const deleteFatLinkModal = $(afatSettings.modal.deleteFatLinkModal.element);
    manageModal(deleteFatLinkModal);
});

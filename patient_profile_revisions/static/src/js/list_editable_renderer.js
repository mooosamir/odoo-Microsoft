odoo.define('patient_profile_revisions.EditableListRenderer', function (require) {
"use strict";

//    var ListRenderer = require('web.EditableListRenderer');
    var ListRenderer = require('web.ListRenderer');
    var dom = require('web.dom');

    ListRenderer.include({
        /**
         * Activates the row at the given row index.
         *
         * @param {integer} rowIndex
         * @returns {Promise}
         */
        _selectCell: function (rowIndex, fieldIndex, options) {
            if (this.__parentedParent.model == 'manufacturer.options.wizard'){
                if (this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.custom_context == 'soft_manufacturer_id'){
                    var req_parent = this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent;
                    for (var i=0; i < req_parent.__parentedChildren.length; i ++){
                        if (req_parent.__parentedChildren[i].name == 'select_soft_base_curve')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[0].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_diameter')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[1].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_color')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[2].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_sphere')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[3].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_cylinder')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[4].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_axis')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[5].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_add_power')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[6].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'select_soft_multifocal')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[7].innerText,undefined);
                    }
                    $('.soft_manufacturer_id_base_curve').val(options.event.currentTarget.parentElement.children[0].innerText);
                    $('.soft_manufacturer_id_diameter').val(options.event.currentTarget.parentElement.children[1].innerText);
                    $('.soft_manufacturer_id_color').val(options.event.currentTarget.parentElement.children[2].innerText);
                    $('.soft_manufacturer_id_sphere').val(options.event.currentTarget.parentElement.children[3].innerText);
                    $('.soft_manufacturer_id_cylinder').val(options.event.currentTarget.parentElement.children[4].innerText);
                    $('.soft_manufacturer_id_axis').val(options.event.currentTarget.parentElement.children[5].innerText);
                    $('.soft_manufacturer_id_add_power').val(options.event.currentTarget.parentElement.children[6].innerText);
                    $('.soft_manufacturer_id_multi_focal').val(options.event.currentTarget.parentElement.children[7].innerText);
                    delete this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent['custom_context'];
                    document.getElementsByClassName('soft_manufacturer_id_base_curve')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_diameter')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_color')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_sphere')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_cylinder')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_axis')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_add_power')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_manufacturer_id_multi_focal')[0].setAttribute('readonly', true);
                    this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.close()
                }
                else if (this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.custom_context == 'soft_left_manufacturer_id'){
                    var req_parent = this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent;
                    for (var i=0; i < req_parent.__parentedChildren.length; i ++){
                        if (req_parent.__parentedChildren[i].name == 'soft_left_base_curve')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[0].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_diameter')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[1].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_color')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[2].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_sphere')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[3].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_cylinder')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[4].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_axis')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[5].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_add_power')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[6].innerText,undefined);
                        if (req_parent.__parentedChildren[i].name == 'soft_left_multifocal')
                            req_parent.__parentedChildren[i]._setValue(options.event.currentTarget.parentElement.children[7].innerText,undefined);
                    }
                    $('.soft_left_manufacturer_id_base_curve').val(options.event.currentTarget.parentElement.children[0].innerText);
                    $('.soft_left_manufacturer_id_diameter').val(options.event.currentTarget.parentElement.children[1].innerText);
                    $('.soft_left_manufacturer_id_color').val(options.event.currentTarget.parentElement.children[2].innerText);
                    $('.soft_left_manufacturer_id_sphere').val(options.event.currentTarget.parentElement.children[3].innerText);
                    $('.soft_left_manufacturer_id_cylinder').val(options.event.currentTarget.parentElement.children[4].innerText);
                    $('.soft_left_manufacturer_id_axis').val(options.event.currentTarget.parentElement.children[5].innerText);
                    $('.soft_left_manufacturer_id_add_power').val(options.event.currentTarget.parentElement.children[6].innerText);
                    $('.soft_left_manufacturer_id_multi_focal').val(options.event.currentTarget.parentElement.children[7].innerText);
                    delete this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent['custom_context'];
                    document.getElementsByClassName('soft_left_manufacturer_id_base_curve')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_diameter')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_color')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_sphere')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_cylinder')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_axis')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_add_power')[0].setAttribute('readonly', true);
                    document.getElementsByClassName('soft_left_manufacturer_id_multi_focal')[0].setAttribute('readonly', true);
                    this.__parentedParent.__parentedParent.__parentedParent.__parentedParent.__parentedParent.close()
                }
            }
            return this._super.apply(this, arguments);
        },

   });

});
odoo.define('openti.website_sale',(require)=>{
  'use strict';

  var sAnimations = require('website.content.snippets.animation');
  var rpc = require('web.rpc');

  sAnimations.registry.WebsiteSale.include({
    events: _.extend({},sAnimations.registry.WebsiteSale.events,{
      'change select[name="state_region_id"]' : '_onChangeRegion',
      'change select[name="state_id"]' : '_onChangeState',
    }),
    _changeCountry: function () {
      this._super();
      if($("select[name='country_id'] option:selected").text().trim() == "Chile"){

        $("select[name='state_id']").val('').parent('div').hide();
        $("select[name='state_id']").data('init', 0);

        rpc.query({
          route:"/shop/country_infos/" + $("#country_id").val(),
          params: {
            mode: 'billing',
          },
        }).then((data) => {

          var selectRegions = $("select[name='state_region_id']")
          if (selectRegions.data('init')===0 || selectRegions.find('option').length===1) {
            if (data.regions.length) {
              selectRegions.html('');
              _.each(data.regions, function (x) {
                var opt = $('<option>').text(x[1])
                .attr('value', x[0])
                .attr('data-code', x[2]);
                selectRegions.append(opt);
              });
              selectRegions.parent('div').show();
            } else {
              selectRegions.val('').parent('div').hide();
            }
            selectRegions.data('init', 0);
          } else {
            selectRegions.data('init', 0);
          }


          });
      }
    },
    _onChangeRegion: (e) => {
      rpc.query({
        route: "/shop/country_infos/" + $("#country_id").val(),
        params: {
            mode: 'billing',
            region: $("select[name='state_region_id']").val(),
        },
      }).then(function (data) {
            // placeholder phone_code
            //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

          // populate states and display
          var selectStates = $("select[name='state_id']");
          // dont reload state at first loading (done in qweb)
          if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
              if (data.states.length) {
                  selectStates.html('');
                  _.each(data.states, function (x) {
                      var opt = $('<option>').text(x[1])
                          .attr('value', x[0])
                          .attr('data-code', x[2]);
                      selectStates.append(opt);
                  });
                  selectStates.parent('div').show();
              } else {
                  selectStates.val('').parent('div').hide();
              }
              selectStates.data('init', 0);
          } else {
              selectStates.data('init', 0);
          }
      });
    },

    _onChangeState: (e) =>{
      rpc.query({
        route:"/shop/country_infos/" + $("#country_id").val(),
        params: {
          mode: 'billing',
          region: $("select[name='state_region_id']").val(),
          state: $("select[name='state_id']").val(),
        },
      }).then((data) => {

        var selectComunas = $("select[name='comuna_id']")
        if (selectComunas.data('init')===0 || selectComunas.find('option').length===1) {
          if (data.cities.length) {
            selectComunas.html('');
            _.each(data.cities, function (x) {
              var opt = $('<option>').text(x[1])
              .attr('value', x[0])
              .attr('data-code', x[2]);
              selectComunas.append(opt);
            });
            selectComunas.parent('div').show();
          } else {
            selectComunas.val('').parent('div').hide();
          }
          selectComunas.data('init', 0);
        } else {
          selectComunas.data('init', 0);
        }



      });

    },

    _
  });

});

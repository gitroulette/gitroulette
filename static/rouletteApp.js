/*global angular:false, $scope:false, console:false */
var app = angular.module('rouletteApp', ["checklist-model", 'ui.bootstrap']);

app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

app.factory('ExistingUrls', function(){
    return { urls: [] };
});
app.controller('submissions', ['$scope', '$http', '$rootScope', 'globalHelpers', function ($scope, $http, $rootScope, globalHelpers) {
    $scope.stats = {};

    $scope.getUrlLanguages = function(gitUrlId){
         globalHelpers.getUrlLanguagesPromise(gitUrlId).then( function (response){
             $scope.stats[gitUrlId] = response.data.languages;
         });
    }

    $scope.addForReview = function () {
        $scope.showWarning = false;
        $scope.showGithubWarning = false;
        if (!$scope.newName || !$scope.newUrl) {
            $scope.showWarning = true;
            return;
        }
        var _new_name = $scope.newName.trim();
        var _new = $scope.newUrl.trim();

        if (!_new || !_new_name) {
            $scope.showWarning = true;
            return;
        }

        if (!_new || !_new_name) {
            $scope.showWarning = true;
            return;
        }

        var _newUrl = globalHelpers.getLocation(_new);
        var pathArray = _newUrl.pathname.split('/');
        isCommit = pathArray.indexOf('commit') > -1;
        isPR = pathArray.indexOf('pull') > -1;

        if (_newUrl.hostname != "github.com" || (!isCommit && !isPR)){
            $scope.showGithubWarning = true;
            return;
        }
        var obj = JSON.parse('{"github_user": "' + $scope.github_user + '", "name": "' + _new_name + '", "url": "' + _new + '"}');
        
        for (var i=0; i < $scope.existing.length; i++){
            if (Object.keys($scope.existing[i])[0] == _new){
                return;
                }
            }
        
        $scope.existing.push(obj);
        
        $http({
            method: "post",
            url: "/new_for_review",
            headers: {'Content-Type': "application/json"},
            data: obj
        }).success(function () {
            // console.log("success!");
        });
        $scope.showUWarning = false;
        $scope.showGithubWarning = false;
        $scope._new = '';
        $rootScope.$broadcast('urlEntryChange', 'args');
    };

    $scope.removeUrl = function (url) {
        if(confirm("Are you sure you want to delete entry \"" + url["name"] + "\"?")){
            for (var i=0; i < $scope.existing.length; i++){
                if ($scope.existing[i]["url"] == url['url']){
                    $scope.existing.splice(i, 1)

                $http({
                    method: "post",
                    url: "/remove_from_list",
                    headers: {'Content-Type': "application/json"},
                    data: url
                }).success(function () {
                    console.log("success!");
                });
                $rootScope.$broadcast('urlEntryChange', 'args');
                }
            }
        }
    };

}]);

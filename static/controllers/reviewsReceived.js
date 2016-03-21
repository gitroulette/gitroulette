app.controller('reviewsReceived', ['$scope', '$http', 'globalHelpers', function ($scope, $http, globalHelpers) {

    $scope.getEntryComment = function(){
        $scope.comments = {};
        //FIXME: check if adding a parameter is worth doing and not get all entries.
        $scope.existing.forEach(function(element){
            var _url = globalHelpers.getLocation(element["url"]);
            var pathArray = _url.pathname.split('/');
            var github_user = pathArray[1];
            var project = pathArray[2];
            var entry_type = pathArray[3];
            var entry_id = pathArray[4];

            if (entry_type == "pull"){
                entry_type = "issue";
            }

            $http({
                method: "get",
                url: "/comments_by_url_id/" + element["id"],
                headers: {'Accept': 'application/json',
                          'Content-Type': "application/json"},
            }).success(function (response) {
                var c = [];
                if(Object.keys($scope.comments).indexOf(project) < 0){
                    $scope.comments[project] = response[project]; 
                } else {
                    $scope.comments[project] = $scope.comments[project].concat(response[project]); 
                }
            });
        });
    };

    $scope.new_something = function (github_user, comment_id){
        var obj = JSON.parse('{"github_user": "' + github_user  + '", "comment_id": "' + comment_id + '"}');
        $http({
            method: "post",
            url: "/new_something",
            headers: {'Accept': 'application/json',
                      'Content-Type': "application/json"},
            data: obj
        }).success(function (response) {
            // console.log(response);
        });
    }

    $scope.noThanks = function (comment_id, url_id){
        var obj = JSON.parse('{"comment_id": "' + comment_id  + '", "url_id": "' + url_id + '"}');
        $http({
            method: "post",
            url: "/decline_comment",
            data: obj,
            headers: {'Accept': 'application/json',
                      'Content-Type': "application/json"},
        }).success(function (response) {
            // console.log(response);
        });
    }
}]);

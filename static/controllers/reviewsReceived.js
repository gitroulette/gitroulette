app.controller('reviewsReceived', ['$scope', '$http', 'globalHelpers', 'ExistingUrls', function ($scope, $http, globalHelpers, ExistingUrls) {

    $scope.$watch(function () { return ExistingUrls.urls }, function (newVal, oldVal) {
        if (typeof newVal !== 'undefined') {
            $scope.getEntryComment();
        }
    });

    $scope.getEntryComment = function(){
        $scope.comments = {};
        //FIXME: check if adding a parameter is worth doing and not get all entries.
        ExistingUrls.urls.forEach(function(element){
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
            }).then(function (response) {
                var c = [];
                if(Object.keys($scope.comments).indexOf(project) < 0){
                    $scope.comments[project] = response.data[project]; 
                } else {
                    $scope.comments[project] = $scope.comments[project].concat(response.data[project]); 
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
        }).then(function (response) {
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
        }).then(function (response) {
            // console.log(response);
        });
    }
}]);

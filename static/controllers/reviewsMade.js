app.controller('reviewsMade', ['$scope', '$http', 'globalHelpers', function ($scope, $http, globalHelpers) {
    $scope.somethings = [];

    $scope.getSomethings = function(github_user){
        $http({
            method: "get",
            url: "/somethings_by_username/" + github_user,
            headers: {'Accept': 'application/json',
                      'Content-Type': "application/json"},
        }).success(function (response) {
            $scope.somethings = response.somethings;
            console.log(response);
        });
    };

}]);

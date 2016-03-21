app.controller('newUser', ['$scope', '$http', 'globalHelpers', '$window', function ($scope, $http, globalHelpers, $window) {
    $scope.comments = [];

    var skills = [];
    $scope.user = {
      skills: []
    };
    $scope.addUserSkills = function(){
        $scope.showWarning = false;
        if ($scope.user['skills'].length == 0) {
            $scope.showWarning = true;
            return;
        }
        $http({
            method: "post",
            url: "/new_github_user",
            headers: {'Content-Type': "application/json"},
            data: $scope.user
        }).success(function () {
            $window.location.href = '/';
            console.log("success!");
        });
    }

    $scope.getUserSkills = function(github_user){
        $http({
            method: "get",
            url: "/skills_by_username/" + github_user,
            headers: {'Accept': 'application/json',
                      'Content-Type': "application/json"},
        }).then(function (response) {
            $scope.chunkedSkills = response.data;
        }); 
    };
}]);

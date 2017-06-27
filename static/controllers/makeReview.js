app.controller('makeReview', function ($scope, $http, $uibModal, $log) {
    $scope.comments = [];

    var skills = [];
    $scope.user = {
        skills: []
    };
    $scope.urlToReview = "No url could be fetched for you to review.";

    $scope.showModal = function(template, urlToReview){
        var items = 22;
        var modalInstance = $uibModal.open({
            animation: true,
            templateUrl: template,
            controller: 'ModalInstanceCtrl',
            controllerAs: '$ctrl',
            bindToController: true,
            size: 'lg',
            resolve: {
                urlToReview: function () {
                    return urlToReview;
                }
            }
        });

        modalInstance.result.then(function (selectedItem) {
            $scope.selected = selectedItem;
        }, function () {
            $log.info('Modal dismissed at: ' + new Date());
        });
    };

    $scope.getUrlToReview = function(template){
        $http({
            method: "get",
            url: "/url_to_review",
            headers: {'Accept': 'application/json',
                      'Content-Type': "application/json"},
        }).then(function (response) {
            $scope.urlToReview = response.data;
            $scope.showModal(template, $scope.urlToReview);
        }); 
    };
});

app.controller('ModalInstanceCtrl', function($scope, $log, $uibModalInstance, urlToReview) {
    this.urlToReview = urlToReview;

    this.ok = function () {
        // TODO: we need to replace this with a "resend" to get a new url for review
        $uibModalInstance.close();
    };

    this.cancel = function () {
        $uibModalInstance.dismiss();
    };
});
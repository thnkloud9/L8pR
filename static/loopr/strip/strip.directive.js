

(function() {
    'use strict';

    StripCtrl.$inject = ['$interval', '$scope', 'Player'];
    function StripCtrl($interval, $scope, Player) {
        var vm = this;

        angular.extend(vm, {
            Player: Player
        })

        // set time
        $interval(function() {
            function checkTime(i) {
                return (i < 10) ? "0" + i : i;
            }
            var today = new Date(),
                h = checkTime(today.getHours()),
                m = checkTime(today.getMinutes());
                vm.time = h + ":" + m;
        }, 2000);
    }

    angular.module('loopr.strip', [])
        .directive('strip', function() {
            return {
                scope: {
                    title: '=',
                    logo: '='
                },
                restrict: 'E',
                controller: StripCtrl,
                controllerAs: 'strip',
                templateUrl: '/static/loopr/strip/strip.html'
            }
        });

})();

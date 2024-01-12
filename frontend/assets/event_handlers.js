//function register_socket_handlers(socket) {
//
//    // Подписываемся на события
//    socket.on('connect', function() {
//        console.log('Connected to the socket server.');
//    });
//
//    socket.on('disconnect', function() {
//        console.log('Disconnected from the socket server.');
//    });
//
//    socket.on('client/categories/list', function(data) {
//        console.log('Event received:', data);
//        handler.go("categories")
//    });
//
//
//}
//
//function socket_load_categories(event){
//
//    socket.emit("server/categories/list", {})
//
//}
//
//
//

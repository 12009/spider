HTTP状态码大全
100-199 用于指定客户端应相应的某些动作。 
200-299 用于表示请求成功。 
300-399 用于已经移动的文件并且常被包含在定位头信息中指定新的地址信息。 
400-499 用于指出客户端的错误。 
500-599 用于支持服务器错误。 

100 (Continue/继续)
101 (Switching Protocols/转换协议)
101 (SC_SWITCHING_PROTOCOLS)状态码是指服务器将按照其上的头信息变为一个不同的协议。这是 HTTP 1.1中新加入的。 

200 (OK/正常)
200 (SC_OK)的意思是一切正常。一般用于相应GET和POST请求。
201 (Created/已创建) (SC_CREATED)表示服务器在请求的响应中建立了新文档；应在定位头信息中给出它的URL。
202 (Accepted/接受) (SC_ACCEPTED)告诉客户端请求正在被执行，但还没有处理完。 
203 (Non-Authoritative Information/非官方信息)状态码  (SC_NON_AUTHORITATIVE_INFORMATION)是表示文档被正常的返回。
204 (No Content/无内容)在并没有新文档的情况下，(SC_NO_CONTENT)确保浏览器继续显示先前的文档。
205 (Reset Content/重置内容)重置内容 (SC_RESET_CONTENT)的意思是虽然没有新文档但浏览器要重置文档显示。这个状态码用于强迫浏览器清除表单域。
206 (Partial Content/局部内容) (SC_PARTIAL_CONTENT)是在服务器完成了一个包含Range头信息的局部请求时被发送的。

300 (Multiple Choices/多重选择) (SC_MULTIPLE_CHOICES)表示被请求的文档可以在多个地方找到，并将在返回的文档中列出来。
301 (Moved Permanently) (SC_MOVED_PERMANENTLY)状态是指所请求的文档在别的地方；文档新的URL会在定位响应头信息中给出。浏览器会自动连接到新的URL。 
302 (Found/找到)与301有些类似，只是定位头信息中所给的URL应被理解为临时交换地址而不是永久的。 
303 (See Other/参见其他信息)这个状态码和 301、302 相似，只是如果最初的请求是 POST，那么新文档（在定位头信息中给出）药用 GET 找回。
304 (Not Modified/为修正)文档缓存，通过提供一个 If-Modified-Since 头信息可指出客户端只希望文档在指定日期之后有所修改时才会重载此文档。
305 (Use Proxy/使用代理) (SC_USE_PROXY)表示所请求的文档要通过定位头信息中的代理服务器获得。
307 (Temporary Redirect/临时重定向)浏览器处理307状态的规则与302相同。

400 (Bad Request/错误请求) (SC_BAD_REQUEST)指出客户端请求中的语法错误。 
401 (Unauthorized/未授权) (SC_UNAUTHORIZED)表示客户端请求未授权。这个响应必须包含一个WWW-Authenticate的授权信息头。
403 (Forbidden/禁止) (SC_FORBIDDEN)的意思是除非拥有授权否则服务器拒绝提供所请求的资源。
404 (Not Found/未找到) (SC_NOT_FOUND)状态每个网络程序员可能都遇到过，他告诉客户端所给的地址无法找到任何资源。
405 (Method Not Allowed/方法未允许) (SC_METHOD_NOT_ALLOWED)指出请求方法(GET, POST, HEAD, PUT, DELETE, 等)对某些特定的资源不允许使用。
406 (Not Acceptable/无法访问) (SC_NOT_ACCEPTABLE)表示请求资源的MIME类型与客户端中Accept头信息中指定的类型不一致。
407 (Proxy Authentication Required/代理服务器认证要求) (SC_PROXY_AUTHENTICATION_REQUIRED)与401状态有些相似，只是这个状态用于代理服务器。
408 (Request Timeout/请求超时) (SC_REQUEST_TIMEOUT)是指服务端等待客户端发送请求的时间过长。
409 (Conflict/冲突)该状态通常与PUT请求一同使用 (SC_CONFLICT)状态常被用于试图上传版本不正确的文件时。
410 (Gone/已经不存在) (SC_GONE)告诉客户端所请求的文档已经不存在并且没有更新的地址。
411 (Length Required/需要数据长度)(SC_LENGTH_REQUIRED)表示服务器不能处理请求，除非客户端发送Content-Length头信息指出发送给服务器的数据的大小。
412 (Precondition Failed/先决条件错误) (SC_PRECONDITION_FAILED)状态指出请求头信息中的某些先决条件是错误的。
413 (Request Entity Too Large/请求实体过大) (SC_REQUEST_ENTITY_TOO_LARGE)告诉客户端现在所请求的文档比服务器现在想要处理的要大。
414 (Request URI Too Long/请求URI过长) (SC_REQUEST_URI_TOO_LONG)状态用于在URI过长的情况时。这里所指的"URI"是指URL中主机、域名及端口号之后的内容。
415 (Unsupported Media Type/不支持的媒体格式) (SC_UNSUPPORTED_MEDIA_TYPE)意味着请求所带的附件的格式类型服务器不知道如何处理。
416 (Requested Range Not Satisfiable/请求范围无法满足)表示客户端包含了一个服务器无法满足的Range头信息的请求。
417 (Expectation Failed/期望失败)如果服务器得到一个带有100-continue值的Expect请求头信息，这是指客户端正在询问是否可以在后面的请求中发送附件。

500 (Internal Server Error/内部服务器错误) (SC_INTERNAL_SERVER_ERROR) 是常用的“服务器错误”状态。
501 (Not Implemented/未实现) (SC_NOT_IMPLEMENTED)状态告诉客户端服务器不支持请求中要求的功能。
502 (Bad Gateway/错误的网关) (SC_BAD_GATEWAY)被用于充当代理或网关的服务器；该状态指出接收服务器接收到远端服务器的错误响应。 
503 (Service Unavailable/服务无法获得)状态码 (SC_SERVICE_UNAVAILABLE)表示服务器由于在维护或已经超载而无法响应。
504 (Gateway Timeout/网关超时)该状态也用于充当代理或网关的服务器；它指出接收服务器没有从远端服务器得到及时的响应。
505 (HTTP Version Not Supported/不支持的 HTTP 版本) (SC_HTTP_VERSION_NOT_SUPPORTED)状态码是说服务器并不支持在请求中所标明 HTTP 版本。


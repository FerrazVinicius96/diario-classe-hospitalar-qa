<?php
/*
 * Router do servidor embutido do PHP para o ambiente local de QA do Diário.
 *
 * config.inc.php escolhe o ambiente pelo HTTP_HOST inteiro: "localhost:8090" cairia
 * no default, que aponta para o Conecta de PRODUÇÃO. Por isso TODAS as constantes do
 * ambiente são definidas aqui antes; o config da aplicação só gera avisos de
 * "already defined" (silenciados) e não troca nada. Nada é editado na aplicação.
 *
 * URL_CONECTA aponta para uma porta local sem serviço: login fora do CPF-sentinela
 * falha por conexão, sem tocar no Conecta de HML nem de produção.
 */

$app = realpath(getenv('QA_APP_DOCROOT') ?: __DIR__ . '/runtime/app-ce1aa37');
if ($app === false) {
	http_response_code(500);
	echo 'Cópia da aplicação não encontrada (QA_APP_DOCROOT).';
	return true;
}

$caminho = rawurldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));
$relativo = ltrim($caminho, '/');

// Mesma exceção do .htaccess: arquivos estáticos saem direto.
if (preg_match('#^(images|public|robots\.txt|css)#', $relativo)) {
	$arquivo = realpath($app . DIRECTORY_SEPARATOR . $relativo);
	if ($arquivo !== false && strpos($arquivo, $app) === 0 && is_file($arquivo)) {
		return false;
	}
}

$_SERVER['SCRIPT_NAME'] = '/index.php';
$_SERVER['PHP_SELF'] = '/index.php';
$_SERVER['SCRIPT_FILENAME'] = $app . DIRECTORY_SEPARATOR . 'index.php';
chdir($app);

define('HTCAMINHO', getenv('QA_DB_HOST') ?: '127.0.0.1');
define('BDCAMINHO', getenv('QA_DB_NAME') ?: 'educ_diariohospitalar_qa');
define('USCAMINHO', getenv('QA_DB_USER') ?: 'root');
define('PSCAMINHO', getenv('QA_DB_PASSWORD') ?: '');
define('IMGCAMINHO', 'http://localhost/api/');
define('ABTCAMINHO', 'local');
define('URL_CONECTA', getenv('QA_URL_CONECTA') ?: 'http://127.0.0.1:8766/');
define('CONECTA_CLIENT_ID', 'admin-diario-hospitalar');
define('CONECTA_CLIENT_SECRET', '');
define('ADMIN_BYPASS_CPF', '00000000000');

$nivel = error_reporting(E_ALL & ~E_WARNING);
require_once $app . DIRECTORY_SEPARATOR . 'config.inc.php';
error_reporting($nivel);

require $app . DIRECTORY_SEPARATOR . 'index.php';

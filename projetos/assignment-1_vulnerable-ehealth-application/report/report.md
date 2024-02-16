# Descrição do projeto

A plataforma representa uma clínica médica onde estão incluídas as seguintes funcionalidades:

1. Criação de contas e inicio de sessão nas mesmas (register.php e login.php)
2. Marcação de consultas (service.php e appointment.php)
3. Visualização de perfil (user.php)
4. Reportar erros por parte de um utlizador (contact.php)
5. Página de administração (admin.php)
6. Leitura de relatórios de consultas (user.php)

## Dicas

Como foi referido no README.md do app/ bem como do app_sec, é crucial aceder à página reset.php.
O reset.php cria várias contas por defeito, seguem-se 3 contas com diferentes permissões

```
1. email: luigi@gmail.com        | password: 1234, utilizador comum
2. email: pedro_doctor@gmail.com | password: 1234, médico
3. email: goncalo@ua.pt          | password: 1234, administrador 
```

Todas as contas criadas tem a permissão "utilizador comum" por defeito, a permissão só pode ser alterada por um administrador na página de administração (admin.php).

## Tecnologia utilizada

De forma a implementar a plataforma, foi utilizado PHP e jQuery. Para geração de relatórios recorreu-se à biblioteca [FPDF](http://www.fpdf.org/).

# Vulnerabilidades

1. SQL Injection
2. XSS
3. Passwords guardadas com pouca segurança
4. Transporte desprotegido de credenciais
5. Insuficiente expiração de sessões
6. Exposição de conteúdo a utilizadores sem permissões suficientes
7. CSRF
8. Previsibilidade do código das consultas
9. Execução de código remoto através de upload de ficheiros

## Score das vulnerabilidades (segundo CVSS)

| Vulnerabilidade                                                       | Score | Vector String                                |
| --------------------------------------------------------------------- | ----- | -------------------------------------------- |
| 1. SQL Injection                                                      | 8.1   | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H |
| 2. XSS                                                                | 4.8   | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N |
| 3. Passwords guardadas com pouca segurança                           | 5.7   | CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N |
| 4. Transporte desprotegido de credenciais                             | 6.3   | CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N |
| 5. Insuficiente expiração de sessões                               | 3.6   | CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N |
| 6. Exposição de conteúdo a utilizadores sem permissõs suficientes | 8.2   | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N |
| 7. CSRF                                                               | 4.3   | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N |
| 8. Previsibilidade do código das consultas                           | 6.5   | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N |
| 9. Execução de código remoto através de upload de ficheiros       | 9.8   | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H |

## 1. Sql injection

### Descrição

Esta vulnerabilidade ocorre quando dados são introduzidos pelo utilizador (em formulários, URLs, ...) e estes venham a ser executados na base de dados. Por exemplo, na criação de utilizador (página register.php) em vez de se colocar texto comum num campo, pode-se inserir queries SQL.

#### Causa

As causas (CWE) desta vulnerabilidade são a CWE-89: "Improper neutralization of special elements in an SQL Command" e a CWE-20: "Improper Input Validation"
Na versão insegura do código não é feita nenhuma validação / tratamento das queries. A correção desta vulnerabilidade tem de ter em conta o tratamento de qualquer query SQL que é feita à base de dados.

#### Possíveis impactos

Caso seja explorada, esta vulnerabilidade pode ter um impacto muito grande na plataforma. Todos os registos da base de dados podem ser apagados (explorado na análise) e/ou informações pessoais de utilizadores podem ser expostas, tais como emails, relatórios de consultas e passwords.

#### Solução

De forma a tratar a vulnerabilidade, para qualquer que seja a query SQL, utiliza-se sempre a seguinte sequência de funções: prepare, bind_param, execute. Estas funções tem a capacidade de detetar e colocar parâmetros na query de forma segura, evitando os ataques por SQL injection.

# 2. XSS

#### Descrição

A página de administração (admin.php) tem uma lista de problemas que foram reportados na página de contactos (contact.php) por utilizadores. O formulário pode ser explorado colocando código executável nele com a tag script. Deste modo, quando um administrador vê a lista de problemas reportados, na verdade o que pode ocorrer é execução de código.

#### Causa

As causas (CWE) desta vulnerabilidade são a CWE-79: "Improper Neutralization of Input During Web Page Generation" e CWE-20: "Improper Input Validation"
Não existe na versão insegura uma verificação de segurança sobre os dados introduzidos no formulário, portanto é possível injetar tags html na página de administração.

#### Possíveis impactos

Esta vulnerabilidade pode ser explorada de várias formas. Uma exploração muito simples é a de injetar um script js, de forma a que a página de administração faça redirect para uma página maliciosa.
Em explorações mais criativas, se partirmos do princípio que o administrador confia na página de administração, o atacante pode injetar um conjunto de CSS+HTML+JS de forma a criar um formulário que o induza a introduzir, por exemplo, dados pessoais que são redirecionados para o atacante. Contudo, esta exploração só funciona se o administrador for informado (de forma maliciosa) que a página de administração foi alterada e que tem de introduzir dados pessoais.

#### Solução

De forma a neutralizar esta vulnerabilidade, recorreu-se à utilização da função [htmlspecialchars](https://www.php.net/manual/en/function.htmlspecialchars.php) do PHP.

## 3. Passwords guardadas com pouca segurança

#### Descrição

No nosso sistema de login e registo, é usada uma hash considerada insegura. O algoritmo utilizado para as passwords é MD5.

#### Causa

A causa (CWE) desta vulnerabilidade é a CWE-916: "Use of Password Hash With Insufficient Computational Effort".
Tendo um pequeno número de bits e sendo conhecidos hash collisions, a hash MD5 é considerada insegura devido à sua facilidade de descodificação com o poder computacional presente atualmente. Além disso, não é utilizado um salt para evitar ataques por rainbow tables. Sem salt, é possível, para cada tentativa, verificar a password de todos os utilizadores em O(1) (assumindo que tem acesso à base de dados).

#### Possíveis impactos

Como a hash usada no nosso sistema é MD5 é possível para um atacante tentar criar hash collisions e conseguir iniciar sessão ou, caso tenha acesso às hashes da base de dados, comparar com hashes conhecidas, podendo descobrir passwords.

#### Solução

Para corrigir esta vulnerabilidade, podemos usar uma hash com um maior comprimento de bits e mais segura, como SHA256, preferencialmente SHA512. Uma maneira ainda mais segura seria usar chaves PBKDF2, que dificultariam em grande dimensão ataques por força bruta. Outra solução seria utilizar salt para cifrar a password introduzida pelo utilizador, com um conjunto de caracteres gerados para cada utilizador. Desta forma, a hash da password de cada utilizador seria sempre diferente, mesmo que as passwords em si fossem iguais. A abordagem escolhida foi a última.

## 4. Transporte desprotegido de credenciais

#### Descrição

Na página login e register, quando as passwords são preenchidas e o formulário é submetido, estas são transportadas sem cifragem, sendo possível utilizar uma aplicação como o wireshark para captar e observar as mesmas.

#### Causa

A causa (CWE) desta vulnerabilidade é a CWE-523: "Unprotected Transport of Credentials".
Não existindo cifragem do lado do cliente nem uso de certificados (HTTPS), a comunicação entre servidor e cliente é feita em plaintext.

#### Possível impacto

Sem cifragem com certificado HTTPS, todo o conteúdo (incluindo password) é transportado pela rede, até ao servidor, em plaintext, sendo possível a qualquer pessoa que interceptar os pacotes observar os dados trasnmitidos.

#### Solução

Para corrigir esta vulnerabilidade, seria apenas preciso usar uma ligação HTTPS por certificado, tornando assim possível, transportar pela rede toda a informação (incluindo passwords) de forma cifrada.

## 5. Insuficiente expiração de sessões

#### Descrição

Para o servidor verificar e manter a sessão de um utilizador, após este a iniciar, são usadas sessões. Estas são verificadas em todas as páginas do site, para garantir a autenticidade e o papel de interação do utilizador. Ao contrário de cookies, estas são guardadas no servidor.
Dada a confidencialidade da informação, as sessões deveriam ter uma duração limitada.

#### Causa

A causa (CWE) desta vulnerabilidade é a CWE-613: "Insufficient Session Expiration".
A duração das sessões não está a ser imposta na versão insegura, o que significa que não expiram automaticamente, ficando assim abertas até o utilizador fazer logout.

#### Possível impacto

Caso o atacante consiga acesso ao computador de um utilizador que tenha iniciado sessão e não a tenha terminado, é possível para o atacante executar ações na conta do mesmo, sem que este tenha conhecimento.

#### Solução

Introduzir um limitador de tempo de sessão, em que quando esse tempo for esgotado, esta seja descartada e o utilizador tenha de voltar a iniciá-la. No nosso caso, o limitador tem uma temporização de 3 minutos, ao final de esse tempo, se o utilizador não tiver navegado pelas páginas, assim se que este interagir com alguma página, a sua sessão vai ser fechada e redirecionado para a página inicial

## 6. Exposição de conteúdo a utilizadores sem permissões suficientes

#### Descrição

Qualquer utilizador autenticado consegue aceder à página de administração (admin.php), mesmo não sendo um administrador. Embora esta página não apareça visível ao utilizador através de um botão na plataforma, esta pode simplesmente ser acedida pelo seguinte url (../admin.php?permission=1).

#### Causa

A causa (CWE) desta vulnerabilidade é a (CWE-497): "Exposure of sensitive system information to an unauthorized control sphere".
Na versão insegura, a validação das permissões desta página é feita através do envio de um campo (permission) no GET, que indica o nível de permissão que o utilizador tem. Caso este seja 1, a página é renderizada ao cliente. Daqui conclui-se que a verificação feita pelo lado do cliente não é suficiente (pode ser manipulada por um atacante).

#### Possíveis impactos

Esta vulnerabilidade implica que qualquer utilizador que tenha o devido conhecimento sobre o accesso à página de administração (parâmetro, no GET,com o nível de permissão a 1), consegue ter acesso a todos os dados pessoais de todos os utilizadores que pertencem à plataforma e consegue alterar as permissões dele próprio tornando-se por exemplo um administrador.

#### Solução

A solução deste problema passou por fazer a validação no lado do servidor em vez de ser pelo parâmetro do GET. Deste modo, o atacante já não é capaz de manipular as permissões.

## 7. CSRF

#### Descrição

O servidor não verifica se um pedido válido e bem formado foi submetido intencionalmente pelo utilizador.

#### Causa

A causa (CWE) desta vulnerabilidade é a CWE-352: "Cross-Site Request Forgery (CSRF)".
Esta acontece quando o servidor recebe um pedido de um utilizador e não tem nenhum mecanismo que verifique se foi enviado pelo próprio utilizador ou por outro com intenções maliciosas.

### Possível impacto

Um atacante pode aliciar o utilizador a clicar em um URL que o redirecione para o nosso servidor, efectuando um pedido GET involuntariamente, usando a sessão do mesmo.

#### Solução

Para corrigir esta vulnerabilidade, é preciso verificar se o token de sessão do utilizador é válido.

## 8. Previsibilidade do código das consultas

#### Descrição

Quando é criada uma consulta é gerado um código que dá acesso à mesma. O código, que começa no valor 1000, é sequencial, ou seja, este valor é incrementado à medida que novas consultas são marcadas.
Sabendo o código da consulta é possível na página do perfil (user.php) ver dados da consulta, incluindo consultas de outros utilizadores.

#### Causa

A causa (CWE) desta vulnerabilidade é a CWE-341: "Predictable from Observable State".
Como o código da consulta é sequencial e baixo (previsível), um utilizador consegue facilmente ter acesso a consultas que não tenham sido marcadas por ele. Outra falha que permite isto, é a inexistência de validação no acesso à consulta, isto é, não se verifica se o utilizador pertence à mesma.

#### Possível impacto

Um atacante com algum conhecimento informático pode marcar 2 consultas e ver que os códigos são sequenciais. Desta forma, este pode experimentar códigos anteriores (ou subsequentes) e consegue ter acesso a todas as consultas marcadas na plataforma, tendo assim acesso a relatórios que incluem dados pessoais dos médicos bem como dos pacientes.

#### Solução

De forma a resolver este problema, alterou-se o algoritmo de geração de códigos. Em vez de sequenciais e baixos, optou-se por uma solução com vários dígitos e caracteres (12 no total) aleatória. Além disso, é verificado se o utilizador esteve envolvido na consulta.

## 9. Execução de código remoto através de upload de ficheiros

#### Descrição

Na plataforma, existe uma funcionalidade para alterar a imagem de perfil do utilizador. A imagem é um ficheiro do sistema de ficheiros do utilizador escolhida pelo mesmo. A verificação do conteúdo é feita pela extensão do ficheiro (apenas são aceites extensões de imagem conhecidas). Por exemplo, um ficheiro que acabe com a substring ".png" é aceite.
No entanto, é possível enviar um ficheiro com o nome "malicius.php.png", que neste caso é aceite pelo servidor e fica guardado no seguinte caminho: images/user_images/{primeiro_nome_do_utilizador}+{número aleatório}+{extensão}. A url pode ser obtida facilmente na página do perfil (onde é mostrada a foto). Esta vulnerabilidade permite a execução de código no servidor enviado por um cliente.

#### Causa

A causa (CWE) deste vulnerabilidade é a CWE-434: "Unrestricted Upload of File with Dangerous Type"
A validação do tipo de ficheiro e a maneira como é guardado são feitos de forma incorreta. Um ficheiro com o nome "malicius.php.png" na versão insegura fica guardado com a extensão ".php". Isto acontece porque, embora o sistema só aceite imagens, este guarda a primeira extensão que encontra, por isso, se submeter-mos um ficheiro "kill_all.php.jpg" (é aceite porque termina com bmp), no servidor fica guardado como kill_all.php, o que permite a execução de código remoto.

#### Possível impacto

Um atacante (como já foi referido na descrição) pode criar um ficheiro com o nome "malicius.php.png" e injetar código php no servidor. Ao aceder à url da suposta imagem, o servidor executa o código que estava guardado no ficheiro enviado, tornando o servidor vulnerável. Pode ocorrer, por exemplo, a criação de uma backdoor que, de forma silenciosa, envia dados sobre a plataforma para o atacante. Com algum esforço, o atacante pode ter acesso ao sistema de ficheiros e obter o código fonte da plataforma, conseguindo assim descobrir as credenciais da base de dados, que consequentemente lhe dá acesso e permissões para tudo na plataforma.

#### Solução

A solução passa por impedir a execução de código remoto. Isto pode ser feito através de uma verificação / alteração da forma como se guarda os ficheiros no servidor. No upload de imagens qualquer ficheiro que não termine com a extensão de imagens e que tenha mais que uma extensão, não pode em situação alguma ser guardado.

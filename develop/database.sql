set global max_connections = 1024;
set autocommit = 0;
set session transaction isolation level read committed;

--
-- 表的结构 `account`
--

CREATE TABLE IF NOT EXISTS `account` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '账户ID',
  `username` varchar(50) NOT NULL DEFAULT '' COMMENT '账号',
  `password` varchar(50) NOT NULL DEFAULT '' COMMENT '密码',
  `rbac_role` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '权限角色',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `rbac_role` (`rbac_role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='账户表' AUTO_INCREMENT=1;

INSERT INTO `account` (`id`, `username`, `password`, `rbac_role`) VALUES (1, 'administrator', '02b6d796814c353a1f0370a416018016', 4294967295);

--
-- 表的结构 `rbac_role`
--

CREATE TABLE IF NOT EXISTS `rbac_role` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `role` varchar(50) NOT NULL DEFAULT '' COMMENT '角色名称',
  `profile` varchar(500) NOT NULL DEFAULT '' COMMENT '角色详情',
  PRIMARY KEY (`id`),
  KEY `role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='RBAC角色' AUTO_INCREMENT=1;

INSERT INTO `rbac_role` (`id`, `role`, profile) VALUES (1, '管理员', '拥有最高权限');

--
-- 表的结构 `rbac_purview`
--

CREATE TABLE IF NOT EXISTS `rbac_purview` (
  `role` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '角色',
  `module` varchar(200) NOT NULL DEFAULT '' COMMENT '权限',
  `purview` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '权限',
  UNIQUE KEY `id` (`role`, `module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='RBAC权限';

INSERT INTO `rbac_purview` (`role`, `module`, `purview`) VALUES (1, 'controller.home.view', 255);

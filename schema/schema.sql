drop table if exists cryptoTotalPricingExt;
drop table if exists cryptoRepoUpdateDatesExt;
drop table if exists cryptoReposExt;
drop table if exists cryptoErrorsExt;
drop table if exists cryptoAllBittrexMarketsExt;

create table cryptoTotalPricingExt (
	cryptoTotalPricingExtId int primary key identity,
	date datetime,
	ticker varchar(255),
	openPrice float(53),
	highPrice float(53),
	lowPrice float(53),
	closePrice float(53),
	volume float(53),
	created datetime default getDate(),
	modified datetime default getDate()

);
create table cryptoRepoUpdateDatesExt (
	cryptoRepoUpdateDatesExtId int primary key identity,
	author varchar(255),
	market varchar(255),
	repoName varchar(255),
	updated datetime,
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoReposExt (
	cryptoReposExtId int primary key identity,
	longName varchar(255),
	repoLocation varchar(255),
	repoName varchar(255),
	shortName varchar(255),
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoErrorsExt (
	cryptoErrorsExtId int primary key identity,
	longName  varchar(255),
	shortName varchar(255),
	error varchar(255),
	output varchar(2555),
	created datetime default getDate(),
	modified datetime default getDate()
);
create table cryptoAllBittrexMarketsExt (
	cryptoAllBittrexMarketsExtId int primary key identity,
	BaseCurrency varchar(255),
	BaseCurrencyLong varchar(255),
	CoinType varchar(255),
	Created datetime,
	IsActive  varchar(255),
	IsRestricted varchar(255),
	IsSponsored varchar(255),
	LogoUrl varchar(255),
	MarketCurrency varchar(255),
	MarketCurrencyLong varchar(255),
	MarketName varchar(255),
	MinTradeSize float(53),
	Notice varchar(2555),
	TxFee float(53),
	createdRecord datetime default getDate(),
	modified datetime default getDate()
);